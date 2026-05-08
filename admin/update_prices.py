"""
Автоматично обновяване на пазарни цени от imot.bg
Пуска се на 9-то число всеки месец от GitHub Actions.

Логика:
  1. За всеки квартал от SCAN_TARGETS → fetch listing страница от imot.bg
  2. Парсва цени и площ → изчислява median €/кв.м
  3. Записва в Supabase таблица `market_prices` с timestamp
  4. Ако scraping-ът fail-не → записва baseline стойностите от locations.py

Изисквания: requests, beautifulsoup4, supabase==1.2.x
"""
from __future__ import annotations

import os
import re
import sys
import time
import logging
import statistics
from datetime import datetime, timezone
from typing import Optional

import requests
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# КОНФИГУРАЦИЯ
# ─────────────────────────────────────────────────────────────

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

# Квартали за сканиране — {display_name: imot.bg URL slug}
SCAN_TARGETS = [
    # Sofia premium
    {"grad": "София", "kvartal": "Лозенец",            "url_path": "grad-sofiya/lozenets/dvustaen"},
    {"grad": "София", "kvartal": "Докторски паметник",  "url_path": "grad-sofiya/doktorski-pametnik/dvustaen"},
    {"grad": "София", "kvartal": "Иван Вазов",          "url_path": "grad-sofiya/ivan-vazov/dvustaen"},
    # Sofia mid-high
    {"grad": "София", "kvartal": "Младост 1",           "url_path": "grad-sofiya/mladost-1/dvustaen"},
    {"grad": "София", "kvartal": "Младост 3",           "url_path": "grad-sofiya/mladost-3/dvustaen"},
    {"grad": "София", "kvartal": "Студентски град",     "url_path": "grad-sofiya/studentski/dvustaen"},
    {"grad": "София", "kvartal": "Дианабад",            "url_path": "grad-sofiya/dianabad/dvustaen"},
    {"grad": "София", "kvartal": "Гео Милев",           "url_path": "grad-sofiya/geo-milev/dvustaen"},
    {"grad": "София", "kvartal": "Малинова долина",     "url_path": "grad-sofiya/malinova-dolina/dvustaen"},
    {"grad": "София", "kvartal": "Кръстова вада",       "url_path": "grad-sofiya/krastova-vada/dvustaen"},
    # Sofia economy
    {"grad": "София", "kvartal": "Люлин 5",             "url_path": "grad-sofiya/lyulin-5/dvustaen"},
    {"grad": "София", "kvartal": "Надежда 2",           "url_path": "grad-sofiya/nadezhda-2/dvustaen"},
    {"grad": "София", "kvartal": "Овча купел 1",        "url_path": "grad-sofiya/ovcha-kupel-1/dvustaen"},
    # Варна
    {"grad": "Варна",   "kvartal": "Бриз",              "url_path": "grad-varna/briz/dvustaen"},
    {"grad": "Варна",   "kvartal": "Младост",           "url_path": "grad-varna/dvustaen"},
    # Пловдив
    {"grad": "Пловдив", "kvartal": "Кършияка",          "url_path": "grad-plovdiv/karshiyaka/dvustaen"},
    {"grad": "Пловдив", "kvartal": "Тракия",            "url_path": "grad-plovdiv/trakiya/dvustaen"},
    # Бургас
    {"grad": "Бургас",  "kvartal": "Лазур",             "url_path": "grad-burgas/lazur/dvustaen"},
]

IMOTBG_BASE = "https://www.imot.bg/obiavi/prodazhbi/"
DELAY_SEC   = 4.0   # пауза между заявки за да не ни блокират
TIMEOUT_SEC = 20
MAX_LISTINGS_PER_PAGE = 30

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "bg-BG,bg;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# ─────────────────────────────────────────────────────────────
# SCRAPING ЛОГИКА
# ─────────────────────────────────────────────────────────────

def _parse_number(text: str) -> Optional[float]:
    """Извлича число от текст: '120 500 лв.' → 120500.0"""
    cleaned = re.sub(r"[^\d.,]", "", text.replace(" ", "").replace("\xa0", ""))
    cleaned = cleaned.replace(",", ".")
    try:
        return float(cleaned)
    except ValueError:
        return None


def _extract_listings(html: str) -> list[dict]:
    """Парсва obявленията от страница на imot.bg.
    Връща list от {"price_eur": float, "sqm": float, "price_sqm": float}
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    # imot.bg използва различни HTML структури исторически.
    # Пробваме два подхода.

    # Подход 1: <div class="price"> + <div class="extra"> (по-нов layout)
    for card in soup.select("div.price-wrap, div.resultItem, li.item"):
        price_el = card.select_one(".price, .resultPrice, span.price")
        area_el  = card.select_one(".area, .resultArea, span.area, .squareMeters")
        if not price_el or not area_el:
            continue

        price_raw = _parse_number(price_el.get_text())
        area_raw  = _parse_number(area_el.get_text())
        if not price_raw or not area_raw or area_raw < 15:
            continue

        # imot.bg след 01.01.2026 показва EUR директно
        # Преди — BGN; конвертираме с курс 1.95583
        price_text = price_el.get_text()
        if "лв" in price_text or "bgn" in price_text.lower():
            price_raw /= 1.95583

        price_sqm = price_raw / area_raw
        if 400 < price_sqm < 8000:   # реалистичен диапазон €/кв.м
            results.append({"price_eur": price_raw, "sqm": area_raw, "price_sqm": round(price_sqm)})

    # Подход 2: намери всички двойки (цена, площ) с regex ако горното не даде резултат
    if not results:
        price_pattern = re.compile(r"(\d[\d\s]{3,7})\s*(?:€|EUR|лв\.?)", re.IGNORECASE)
        area_pattern  = re.compile(r"(\d{2,4})\s*(?:кв\.?\s*м|m²)", re.IGNORECASE)

        prices = [_parse_number(m.group(1)) for m in price_pattern.finditer(html)]
        areas  = [_parse_number(m.group(1)) for m in area_pattern.finditer(html)]

        for p, a in zip(prices, areas):
            if p and a and a >= 15:
                price_sqm = p / a
                if 400 < price_sqm < 8000:
                    results.append({"price_eur": p, "sqm": a, "price_sqm": round(price_sqm)})

    return results[:MAX_LISTINGS_PER_PAGE]


def scrape_neighborhood(url_path: str) -> Optional[int]:
    """Fetch imot.bg страница и върни median €/кв.м или None при грешка."""
    url = IMOTBG_BASE + url_path + "/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        listings = _extract_listings(resp.text)
        if len(listings) < 3:
            log.warning(f"Малко обяви ({len(listings)}) за {url_path}")
            return None
        prices_sqm = [l["price_sqm"] for l in listings]
        median_val = int(statistics.median(prices_sqm))
        log.info(f"  {url_path}: {len(listings)} обяви, median={median_val} €/кв.м")
        return median_val
    except Exception as e:
        log.warning(f"  Грешка при {url_path}: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# SUPABASE ЗАПИС
# ─────────────────────────────────────────────────────────────

def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL и SUPABASE_KEY трябва да са зададени като env variables."
        )
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upsert_price(sb, grad: str, kvartal: str, avg_sqm: int,
                 listings_count: int, source: str) -> None:
    """Записва или обновява цена в таблица market_prices."""
    sb.table("market_prices").upsert(
        {
            "grad": grad,
            "kvartal": kvartal,
            "avg_sqm": avg_sqm,
            "listings_count": listings_count,
            "source": source,
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        },
        on_conflict="grad,kvartal",
    ).execute()


def upsert_baseline_prices(sb) -> None:
    """Записва baseline стойностите от locations.py ако scraping-ът fail-не."""
    # Добавяме пакета само ако сме в правилната директория
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    try:
        from utils.locations import LOCATIONS
    except ImportError:
        log.error("Не може да се зареди utils/locations.py — пропускаме baseline.")
        return

    count = 0
    for grad, city_data in LOCATIONS.items():
        for kvartal, zone_data in city_data["zones"].items():
            upsert_price(
                sb,
                grad=grad,
                kvartal=kvartal,
                avg_sqm=zone_data["avg_sqm"],
                listings_count=0,
                source="baseline_locations_py",
            )
            count += 1

    log.info(f"Записани {count} baseline стойности от locations.py.")


# ─────────────────────────────────────────────────────────────
# ГЛАВНА ФУНКЦИЯ
# ─────────────────────────────────────────────────────────────

def main():
    log.info("=== Стартиране на обновяване на цени ===")
    log.info(f"Дата: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")

    try:
        sb = get_supabase()
        log.info("Supabase: свързан успешно.")
    except Exception as e:
        log.error(f"Supabase грешка: {e}")
        sys.exit(1)

    # Фаза 1: Запиши baseline стойности (за всички квартали)
    log.info("Фаза 1: Записване на baseline стойности...")
    upsert_baseline_prices(sb)

    # Фаза 2: Scraping на imot.bg за актуални цени
    log.info(f"Фаза 2: Scraping на {len(SCAN_TARGETS)} квартала от imot.bg...")
    success_count = 0
    fail_count    = 0

    for target in SCAN_TARGETS:
        log.info(f"Обработвам: {target['grad']} / {target['kvartal']}")
        median_sqm = scrape_neighborhood(target["url_path"])

        if median_sqm:
            try:
                upsert_price(
                    sb,
                    grad=target["grad"],
                    kvartal=target["kvartal"],
                    avg_sqm=median_sqm,
                    listings_count=MAX_LISTINGS_PER_PAGE,
                    source="imot.bg",
                )
                success_count += 1
            except Exception as e:
                log.error(f"  Грешка при запис в Supabase: {e}")
                fail_count += 1
        else:
            log.warning(f"  Пропускаме {target['kvartal']} — запазена е baseline стойността.")
            fail_count += 1

        time.sleep(DELAY_SEC)

    log.info("=== Завършено ===")
    log.info(f"Успешни: {success_count} / Неуспешни: {fail_count}")

    if fail_count == len(SCAN_TARGETS):
        log.error("ВСИЧКИ scraping заявки fail-наха! Проверете дали imot.bg е достъпен.")
        sys.exit(1)


if __name__ == "__main__":
    main()
