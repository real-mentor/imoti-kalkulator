"""
Автоматично обновяване на пазарни цени от imot.bg
Пуска се на 9-то число всеки месец от GitHub Actions,
или ръчно: python admin/update_prices.py

Логика:
  Фаза 1 (винаги): Записва baseline стойности от utils/locations.py
  Фаза 2 (бонус):  Scraping на imot.bg → актуализира само квартали с достатъчно обяви

При блокиран scraping — завършва с exit 0 (baseline е запазен, нищо не се чупи).
При Supabase грешка — завършва с exit 1 (критично).

HTML структура на imot.bg (верифицирана май 2026):
  Encoding:     Windows-1251
  Listing:      div.item
  Цена (EUR):   div.price > div  →  "230 000 €\n449 840.90 лв."
  Площ:         div.info  →  regex (\d+)\s*кв\.м
"""
from __future__ import annotations

import os
import re
import sys
import time
import random
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

# Ако стартираме локално без env → зареди .env файла
if not SUPABASE_URL or not SUPABASE_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
        SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
        SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
    except ImportError:
        pass

IMOTBG_BASE = "https://www.imot.bg"
DELAY_SEC   = (4.0, 8.0)   # случаен интервал между заявки
TIMEOUT_SEC = 25
MIN_LISTINGS = 4            # минимум обяви за валиден резултат

# Ротация на User-Agent headers (имитира различни браузъри)
USER_AGENTS = [
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/17.4 Safari/605.1.15"
    ),
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:125.0) "
        "Gecko/20100101 Firefox/125.0"
    ),
]

# Квартали за сканиране — SEO URL формат (верифициран от реален fetch)
SCAN_TARGETS = [
    # Sofia premium
    {"grad": "София", "kvartal": "Лозенец",           "path": "/obiavi/prodazhbi/grad-sofiya/lozenets/dvustaen/"},
    {"grad": "София", "kvartal": "Докторски паметник", "path": "/obiavi/prodazhbi/grad-sofiya/doktorski-pametnik/dvustaen/"},
    {"grad": "София", "kvartal": "Иван Вазов",         "path": "/obiavi/prodazhbi/grad-sofiya/ivan-vazov/dvustaen/"},
    {"grad": "София", "kvartal": "Изток",              "path": "/obiavi/prodazhbi/grad-sofiya/iztok/dvustaen/"},
    {"grad": "София", "kvartal": "Стрелбище",          "path": "/obiavi/prodazhbi/grad-sofiya/strelbishte/dvustaen/"},
    # Sofia mid-high
    {"grad": "София", "kvartal": "Младост 1",          "path": "/obiavi/prodazhbi/grad-sofiya/mladost-1/dvustaen/"},
    {"grad": "София", "kvartal": "Младост 3",          "path": "/obiavi/prodazhbi/grad-sofiya/mladost-3/dvustaen/"},
    {"grad": "София", "kvartal": "Студентски град",    "path": "/obiavi/prodazhbi/grad-sofiya/studentski/dvustaen/"},
    {"grad": "София", "kvartal": "Дианабад",           "path": "/obiavi/prodazhbi/grad-sofiya/dianabad/dvustaen/"},
    {"grad": "София", "kvartal": "Гео Милев",          "path": "/obiavi/prodazhbi/grad-sofiya/geo-milev/dvustaen/"},
    {"grad": "София", "kvartal": "Малинова долина",    "path": "/obiavi/prodazhbi/grad-sofiya/malinova-dolina/dvustaen/"},
    {"grad": "София", "kvartal": "Кръстова вада",      "path": "/obiavi/prodazhbi/grad-sofiya/krastova-vada/dvustaen/"},
    {"grad": "София", "kvartal": "Дружба 1",           "path": "/obiavi/prodazhbi/grad-sofiya/druzhba-1/dvustaen/"},
    # Sofia economy
    {"grad": "София", "kvartal": "Люлин 5",            "path": "/obiavi/prodazhbi/grad-sofiya/lyulin-5/dvustaen/"},
    {"grad": "София", "kvartal": "Надежда 2",          "path": "/obiavi/prodazhbi/grad-sofiya/nadezhda-2/dvustaen/"},
    {"grad": "София", "kvartal": "Овча купел 1",       "path": "/obiavi/prodazhbi/grad-sofiya/ovcha-kupel-1/dvustaen/"},
    # Варна
    {"grad": "Варна",   "kvartal": "Бриз",             "path": "/obiavi/prodazhbi/grad-varna/briz/dvustaen/"},
    {"grad": "Варна",   "kvartal": "Левски",           "path": "/obiavi/prodazhbi/grad-varna/levski/dvustaen/"},
    # Пловдив
    {"grad": "Пловдив", "kvartal": "Кършияка",         "path": "/obiavi/prodazhbi/grad-plovdiv/karshiyaka/dvustaen/"},
    {"grad": "Пловдив", "kvartal": "Тракия",           "path": "/obiavi/prodazhbi/grad-plovdiv/trakiya/dvustaen/"},
    # Бургас
    {"grad": "Бургас",  "kvartal": "Лазур",            "path": "/obiavi/prodazhbi/grad-burgas/lazur/dvustaen/"},
    {"grad": "Бургас",  "kvartal": "Славейков",        "path": "/obiavi/prodazhbi/grad-burgas/slaveykov/dvustaen/"},
]


# ─────────────────────────────────────────────────────────────
# HTTP СЕСИЯ
# ─────────────────────────────────────────────────────────────

def build_session() -> requests.Session:
    """Създава сесия с cookies от началната страница на imot.bg."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "bg-BG,bg;q=0.9,en;q=0.8",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    })
    try:
        log.info("Инициализиране на сесия с imot.bg...")
        resp = session.get(IMOTBG_BASE, timeout=TIMEOUT_SEC)
        resp.raise_for_status()
        log.info(f"  Cookies получени: {list(session.cookies.keys())}")
    except Exception as e:
        log.warning(f"  Не може да се вземат начални cookies: {e}")
    return session


# ─────────────────────────────────────────────────────────────
# HTML ПАРСИРАНЕ
# ─────────────────────────────────────────────────────────────

def _parse_eur(price_tag) -> Optional[float]:
    """Извлича EUR от <div class="price"><div>230 000 €\n449 840.90 лв.</div></div>"""
    if not price_tag:
        return None
    text = price_tag.get_text()
    # Взимаме частта преди "€"
    if "€" in text:
        raw = text.split("€")[0].strip()
    elif "EUR" in text.upper():
        raw = text.upper().split("EUR")[0].strip()
    else:
        return None
    digits = re.sub(r"[^\d]", "", raw)
    return float(digits) if digits else None


def _parse_sqm(info_tag) -> Optional[float]:
    """Извлича кв.м от div.info: '65 кв.м, 2-ри ет. от 5, ...'"""
    if not info_tag:
        return None
    m = re.search(r"(\d{2,4})\s*кв\.?\s*м", info_tag.get_text())
    return float(m.group(1)) if m else None


def parse_listings(html: str) -> list[dict]:
    """Парсва всички обяви от страница на imot.bg.
    Декодира Windows-1251 → трябва да се подаде raw bytes или вече декодиран string.
    Връща list от {"price_eur": float, "sqm": float, "price_sqm": int}
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for item in soup.select("div.item"):
        price_tag = item.select_one("div.price > div")
        info_tag  = item.select_one("div.info")

        price = _parse_eur(price_tag)
        sqm   = _parse_sqm(info_tag)

        if not price or not sqm:
            continue
        if sqm < 15 or sqm > 600:
            continue

        price_sqm = price / sqm
        if 400 < price_sqm < 10_000:   # реалистичен диапазон €/кв.м
            results.append({
                "price_eur": price,
                "sqm": sqm,
                "price_sqm": int(price_sqm),
            })

    return results


# ─────────────────────────────────────────────────────────────
# SCRAPING НА КВАРТАЛ
# ─────────────────────────────────────────────────────────────

def scrape_neighborhood(session: requests.Session, path: str) -> Optional[int]:
    """Fetch страница и върни median €/кв.м или None при грешка/блокиране."""
    url = IMOTBG_BASE + path
    # Ротирай User-Agent при всяка заявка
    session.headers["User-Agent"] = random.choice(USER_AGENTS)

    try:
        resp = session.get(url, timeout=TIMEOUT_SEC)

        # Проверка за блокиране (403, 429, captcha)
        if resp.status_code in (403, 429):
            log.warning(f"  Блокиран (HTTP {resp.status_code}): {path}")
            return None
        if resp.status_code != 200:
            log.warning(f"  HTTP {resp.status_code}: {path}")
            return None

        # imot.bg encode: Windows-1251
        html = resp.content.decode("windows-1251", errors="replace")

        # Проверка за captcha страница
        if "captcha" in html.lower() or "robot" in html.lower():
            log.warning(f"  Captcha/robot detection: {path}")
            return None

        listings = parse_listings(html)

        if len(listings) < MIN_LISTINGS:
            log.warning(f"  Малко обяви ({len(listings)} < {MIN_LISTINGS}) за {path}")
            return None

        prices = [l["price_sqm"] for l in listings]
        median = int(statistics.median(prices))
        log.info(f"  OK: {len(listings)} обяви, median = {median} €/кв.м")
        return median

    except requests.exceptions.Timeout:
        log.warning(f"  Timeout: {path}")
        return None
    except requests.exceptions.ConnectionError:
        log.warning(f"  Connection error: {path}")
        return None
    except Exception as e:
        log.warning(f"  Грешка: {e}")
        return None


# ─────────────────────────────────────────────────────────────
# SUPABASE
# ─────────────────────────────────────────────────────────────

def get_supabase():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError(
            "SUPABASE_URL и SUPABASE_KEY не са зададени.\n"
            "Локално: уверете се, че .env файлът съществува.\n"
            "GitHub Actions: добавете Secrets в Settings → Secrets → Actions."
        )
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def upsert_price(sb, grad: str, kvartal: str, avg_sqm: int,
                 listings_count: int, source: str) -> None:
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


def save_baseline(sb) -> int:
    """Записва всички baseline стойности от locations.py. Връща брой записи."""
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
    try:
        from utils.locations import LOCATIONS
    except ImportError as e:
        log.error(f"Не може да се зареди utils/locations.py: {e}")
        return 0

    count = 0
    for grad, city_data in LOCATIONS.items():
        for kvartal, zone_data in city_data["zones"].items():
            try:
                upsert_price(sb, grad, kvartal,
                             avg_sqm=zone_data["avg_sqm"],
                             listings_count=0,
                             source="baseline_locations_py")
                count += 1
            except Exception as e:
                log.warning(f"  Грешка при запис {grad}/{kvartal}: {e}")
    return count


# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    log.info("=" * 55)
    log.info("  Real Mentor — Обновяване на пазарни цени")
    log.info(f"  {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    log.info("=" * 55)

    # ── Свържи се с Supabase (критично — при грешка → exit 1) ──
    try:
        sb = get_supabase()
        log.info("Supabase: свързан успешно.")
    except Exception as e:
        log.error(f"КРИТИЧНА ГРЕШКА — Supabase: {e}")
        sys.exit(1)

    # ── Фаза 1: Baseline (винаги работи) ──────────────────────
    log.info("")
    log.info("▶ Фаза 1: Запис на baseline стойности...")
    baseline_count = save_baseline(sb)
    log.info(f"  Записани {baseline_count} baseline записа.")

    # ── Фаза 2: Scraping (бонус — при неуспех exit 0) ─────────
    log.info("")
    log.info(f"▶ Фаза 2: Scraping на {len(SCAN_TARGETS)} квартала от imot.bg...")

    session = build_session()
    success, failed = 0, 0

    for target in SCAN_TARGETS:
        log.info(f"  {target['grad']} / {target['kvartal']}")
        delay = random.uniform(*DELAY_SEC)
        time.sleep(delay)

        median_sqm = scrape_neighborhood(session, target["path"])

        if median_sqm:
            try:
                upsert_price(sb,
                             grad=target["grad"],
                             kvartal=target["kvartal"],
                             avg_sqm=median_sqm,
                             listings_count=MIN_LISTINGS,
                             source="imot.bg")
                success += 1
            except Exception as e:
                log.error(f"  Supabase грешка при запис: {e}")
                failed += 1
        else:
            log.info(f"  → Пропуснат, baseline стойността е запазена.")
            failed += 1

    # ── Резюме ────────────────────────────────────────────────
    log.info("")
    log.info("=" * 55)
    if success > 0:
        log.info(f"✅ Scraping: {success} успешни, {failed} пропуснати.")
        log.info("   Актуалните цени са записани в Supabase.")
    else:
        log.info("⚠️  Scraping неуспешен (всички квартали са пропуснати).")
        log.info("   Причина: imot.bg блокира заявките (очаквано от CI/CD).")
        log.info("   Baseline стойностите от locations.py са запазени.")
        log.info("   За актуални цени пусни скрипта ЛОКАЛНО от твоя Mac.")
    log.info(f"   Baseline: {baseline_count} квартала в Supabase.")
    log.info("=" * 55)

    # Винаги exit 0 — baseline е успешен, scraping е бонус
    sys.exit(0)


if __name__ == "__main__":
    main()
