"""
Финансови изчисления — всички формули за 7-те стратегии.
Всичко в EUR. Python 3.9+ съвместимо.
"""
from __future__ import annotations
import math
from typing import Optional, List, Dict, Any
from utils.market_data import (
    VACANCY_RATE,
    ZASTRAKHOVKA_GOD_PCT,
    DANUK_IMOT_GOD_PCT,
    DANUK_NAEM_PCT,
    FIX_FLIP_PRAVILO_70,
    FIX_FLIP_PRODAJBA_RAZKHODI,
    FIX_FLIP_SROK_REMONT_MES,
    FIX_FLIP_SROK_PRODAJBA_MES,
    FIX_FLIP_ROI_OTLICHNA,
    FIX_FLIP_ROI_DOBRA,
    FIX_FLIP_ROI_PRIEMLIVА,
    REMONT_REZERV_PCT,
    BUY_HOLD_OPERATIVNI_PCT,
)
from utils.price_model import badeshta_cena, badeshta_cena_po_godini


# ─────────────────────────────────────────
# КРЕДИТНИ ИЗЧИСЛЕНИЯ
# ─────────────────────────────────────────

def mesechna_vnоska(kredit: float, lihva_god: float, srok_god: int) -> float:
    """Месечна анюитетна вноска по кредит."""
    if kredit <= 0 or srok_god <= 0:
        return 0.0
    r = lihva_god / 12
    n = srok_god * 12
    if r == 0:
        return kredit / n
    return kredit * r * (1 + r) ** n / ((1 + r) ** n - 1)


def kreditna_ostatok(kredit: float, lihva_god: float, srok_god: int, plateni_meseci: int) -> float:
    """Остатъчна главница след N платени месеца."""
    if kredit <= 0 or srok_god <= 0:
        return 0.0
    r = lihva_god / 12
    n = srok_god * 12
    m = plateni_meseci
    if r == 0:
        return max(0.0, kredit - kredit / n * m)
    return kredit * ((1 + r) ** n - (1 + r) ** m) / ((1 + r) ** n - 1)


def obshto_plateno_po_kredit(kredit: float, lihva_god: float, srok_god: int) -> float:
    """Общо платено по кредита за целия срок."""
    return mesechna_vnоska(kredit, lihva_god, srok_god) * srok_god * 12


# ─────────────────────────────────────────
# НАЕМ — ОПЕРАЦИОННИ МЕТРИКИ
# ─────────────────────────────────────────

def noi(
    mesecen_naem: float,
    cena_imot: float,
    vacancy: Optional[float] = None,
    zastrakhovka_pct: Optional[float] = None,
    danuk_pct: Optional[float] = None,
) -> float:
    """
    Net Operating Income (NOI) — годишен нетен оперативен доход.
    Разходи: застраховка + данък имот (% от имота) + данък наем 9% (от наема).
    """
    vac = vacancy if vacancy is not None else VACANCY_RATE
    zast = zastrakhovka_pct if zastrakhovka_pct is not None else ZASTRAKHOVKA_GOD_PCT
    dan = danuk_pct if danuk_pct is not None else DANUK_IMOT_GOD_PCT

    god_naem = mesecen_naem * 12 * (1 - vac)
    razkhodi = (
        cena_imot * zast
        + cena_imot * dan
        + mesecen_naem * 12 * DANUK_NAEM_PCT
    )
    return god_naem - razkhodi


def cap_rate(noi_val: float, cena_imot: float) -> float:
    """Cap Rate = NOI / цена × 100%"""
    if cena_imot <= 0:
        return 0.0
    return (noi_val / cena_imot) * 100


def cash_on_cash(
    mesecen_naem: float,
    cena_imot: float,
    mesechna_ipoteka: float,
    samoychastie_eur: float,
    vacancy: Optional[float] = None,
) -> float:
    """
    Cash-on-Cash Return = годишен нетен паричен поток / вложен капитал × 100%
    """
    vac = vacancy if vacancy is not None else VACANCY_RATE
    god_naem = mesecen_naem * 12 * (1 - vac)
    god_ipoteka = mesechna_ipoteka * 12
    god_razkhodi = cena_imot * (ZASTRAKHOVKA_GOD_PCT + DANUK_IMOT_GOD_PCT) + mesecen_naem * 12 * DANUK_NAEM_PCT
    net_cf = god_naem - god_ipoteka - god_razkhodi
    if samoychastie_eur <= 0:
        return 0.0
    return (net_cf / samoychastie_eur) * 100


def mesecen_pаricen_potok(
    mesecen_naem: float,
    cena_imot: float,
    mesechna_ipoteka: float,
    vacancy: Optional[float] = None,
) -> float:
    """Месечен паричен поток (наем - вноска - разходи/12)."""
    vac = vacancy if vacancy is not None else VACANCY_RATE
    god_razkhodi_mes = (
        cena_imot * (ZASTRAKHOVKA_GOD_PCT + DANUK_IMOT_GOD_PCT) / 12
        + mesecen_naem * DANUK_NAEM_PCT
    )
    return mesecen_naem * (1 - vac) - mesechna_ipoteka - god_razkhodi_mes


def payback_period(
    samoychastie_eur: float,
    notarialni_eur: float,
    remont_eur: float,
    mesecen_cf: float,
) -> Optional[float]:
    """Срок за пълна възвръщаемост в месеци. None ако паричният поток е отрицателен."""
    total_vlozhenie = samoychastie_eur + notarialni_eur + remont_eur
    if mesecen_cf <= 0:
        return None
    return total_vlozhenie / mesecen_cf


# ─────────────────────────────────────────
# СТРАТЕГИЯ 5 — FIX & FLIP
# ─────────────────────────────────────────

def fix_flip_analiz(
    pokupna: float,
    remont: float,
    arv: float,
    notarialni_pct: float = 0.03,
    prodajbeni_pct: Optional[float] = None,
    srok_remont_mes: Optional[int] = None,
    srok_prodajba_mes: Optional[int] = None,
) -> Dict[str, Any]:
    """Пълен Fix & Flip анализ."""
    prod_pct = prodajbeni_pct if prodajbeni_pct is not None else FIX_FLIP_PRODAJBA_RAZKHODI
    sr_rem = srok_remont_mes if srok_remont_mes is not None else FIX_FLIP_SROK_REMONT_MES
    sr_prod = srok_prodajba_mes if srok_prodajba_mes is not None else FIX_FLIP_SROK_PRODAJBA_MES

    razkhodi_pokupka = pokupna * notarialni_pct
    razkhodi_prodajba = arv * prod_pct
    obshto_vlozhenie = pokupna + razkhodi_pokupka + remont

    brutna_pechalba = arv - obshto_vlozhenie - razkhodi_prodajba
    roi_pct = (brutna_pechalba / obshto_vlozhenie) * 100 if obshto_vlozhenie > 0 else 0.0
    obshto_srok_mes = sr_rem + sr_prod

    # Правило 70%
    max_pokupna_70 = arv * FIX_FLIP_PRAVILO_70 - remont
    pravilo_70_ok = pokupna <= max_pokupna_70

    # Оценка
    if roi_pct >= FIX_FLIP_ROI_OTLICHNA * 100:
        otsenka = "ОТЛИЧНА"
        otsenka_emoji = "✅"
    elif roi_pct >= FIX_FLIP_ROI_DOBRA * 100:
        otsenka = "ДОБРА"
        otsenka_emoji = "✅"
    elif roi_pct >= FIX_FLIP_ROI_PRIEMLIVА * 100:
        otsenka = "ПРИЕМЛИВА"
        otsenka_emoji = "⚠️"
    else:
        otsenka = "ЛОША"
        otsenka_emoji = "❌"

    return {
        "pokupna": pokupna,
        "razkhodi_pokupka": razkhodi_pokupka,
        "remont": remont,
        "remont_s_rezerv": remont * (1 + REMONT_REZERV_PCT),
        "obshto_vlozhenie": obshto_vlozhenie,
        "arv": arv,
        "razkhodi_prodajba": razkhodi_prodajba,
        "brutna_pechalba": brutna_pechalba,
        "roi_pct": roi_pct,
        "obshto_srok_mes": obshto_srok_mes,
        "max_pokupna_70": max_pokupna_70,
        "pravilo_70_ok": pravilo_70_ok,
        "otsenka": otsenka,
        "otsenka_emoji": otsenka_emoji,
    }


# ─────────────────────────────────────────
# СТРАТЕГИЯ 6 — BUY & HOLD
# ─────────────────────────────────────────

def buy_hold_analiz(
    pokupna: float,
    etap: str,
    mesecen_naem: float,
    samoychastie_pct: float,
    lihva: float,
    srok_god: int,
    notarialni_pct: float = 0.03,
    remont_eur: float = 0.0,
    max_godini: int = 10,
    pazarno_poskapvane: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Buy & Hold анализ — стойност, натрупан наем, капиталов резултат по години.

    Ценови ръст: PAZARNO_POSKAPVANE_GOD = 7% номинален (инфлацията е включена).
    Оперативни разходи от стойността на имота:
      1.0% ремонтен резерв + 0.1% данък имот + 0.2% застраховка = 1.3%/год
    """
    samoych = pokupna * samoychastie_pct
    kredit = pokupna * (1 - samoychastie_pct)
    notarialni = pokupna * notarialni_pct
    vnоska = mesechna_vnоska(kredit, lihva, srok_god)

    # Разходи за притежание: данък имот + застраховка (% от имота) + данък наем 9%
    vac = BUY_HOLD_OPERATIVNI_PCT["vacancy"]           # 5% незаетост
    pct_imot = (
        BUY_HOLD_OPERATIVNI_PCT["danuk_imot"]          # 0.1% данък имот
        + BUY_HOLD_OPERATIVNI_PCT["zastrakhovka"]      # 0.2% застраховка
    )                                                   # = 0.3% от pokupna/год
    operativni_god = (
        pokupna * pct_imot
        + mesecen_naem * 12 * DANUK_NAEM_PCT           # 9% данък доход от наем
    )

    stojnosti = badeshta_cena_po_godini(pokupna, etap, max_godini, pazarno_poskapvane)

    rezultati = []
    natrupen_naem = 0.0
    for g in range(max_godini + 1):
        god_naem_neto = mesecen_naem * 12 * (1 - vac) - operativni_god
        natrupen_naem += god_naem_neto if g > 0 else 0
        ostatok_kredit = kreditna_ostatok(kredit, lihva, srok_god, g * 12)
        kapital_v_imot = stojnosti[g] - ostatok_kredit

        nachaln_vlozhenie = samoych + notarialni + remont_eur
        kapitalov_rezultat = stojnosti[g] + natrupen_naem - ostatok_kredit - nachaln_vlozhenie
        roi_pct = (kapitalov_rezultat / nachaln_vlozhenie * 100) if nachaln_vlozhenie > 0 else 0.0
        godishen_roi = ((1 + roi_pct / 100) ** (1 / max(g, 0.001)) - 1) * 100 if g > 0 else 0.0

        rezultati.append({
            "godina": g,
            "stojnost_imot": stojnosti[g],
            "natrupen_naem": natrupen_naem,
            "ostatok_kredit": ostatok_kredit,
            "kapital_v_imot": kapital_v_imot,
            "kapitalov_rezultat": kapitalov_rezultat,
            "roi_pct": roi_pct,
            "godishen_roi": godishen_roi,
        })

    god_naem_bruto = mesecen_naem * 12
    god_naem_neto = god_naem_bruto * (1 - vac) - operativni_god

    return {
        "pokupna": pokupna,
        "samoychastie": samoych,
        "kredit": kredit,
        "notarialni": notarialni,
        "remont": remont_eur,
        "nachaln_vlozhenie": samoych + notarialni + remont_eur,
        "mesechna_vnоska": vnоska,
        "mesecen_naem": mesecen_naem,
        "god_naem_bruto": god_naem_bruto,
        "god_naem_neto": god_naem_neto,
        "operativni_razkhodi": operativni_god,
        "po_godini": rezultati,
    }


# ─────────────────────────────────────────
# ПРОФИЛ НА ИНВЕСТИТОРА — КРЕДИТЕН КАПАЦИТЕТ
# ─────────────────────────────────────────

def kreditен_kapacitet(
    neto_dohod: float,
    partnyor_dohod: float = 0.0,
    drugi_dohodi: float = 0.0,
    mesechni_razkhodi: float = 0.0,
    tekushti_krediti: float = 0.0,
    lihva: Optional[float] = None,
    srok_god: int = 25,
    samoychastie_pct: float = 0.20,
) -> Dict[str, Any]:
    """Изчислява максималния ипотечен кредит за дадения профил."""
    from utils.market_data import LIHVA_DEFAULT, MAX_VNОSKA_PCT_OT_DOHOD

    lih = lihva if lihva is not None else LIHVA_DEFAULT
    obshto_dohod = neto_dohod + partnyor_dohod + drugi_dohodi
    svobodna_suma = obshto_dohod - mesechni_razkhodi - tekushti_krediti
    max_vnоska = svobodna_suma * MAX_VNОSKA_PCT_OT_DOHOD

    # Обратна формула: от вноска → кредит
    r = lih / 12
    n = srok_god * 12
    if max_vnоska <= 0:
        max_kredit = 0.0
    elif r == 0:
        max_kredit = max_vnоska * n
    else:
        max_kredit = max_vnоska * ((1 + r) ** n - 1) / (r * (1 + r) ** n)

    max_imot = max_kredit / (1 - samoychastie_pct) if samoychastie_pct < 1 else 0.0
    nujno_samoychastie = max_imot * samoychastie_pct

    return {
        "obshto_dohod": obshto_dohod,
        "svobodna_suma": svobodna_suma,
        "max_vnоska": max_vnоska,
        "max_kredit": max_kredit,
        "max_imot": max_imot,
        "nujno_samoychastie": nujno_samoychastie,
    }
