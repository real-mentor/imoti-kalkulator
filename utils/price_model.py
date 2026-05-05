"""
Модел за бъдеща цена на имот.
Формула: Бъдеща_цена = Покупна × (1+инфл)^г × (1+пазар)^г × прогрес_коеф
"""
from __future__ import annotations
from typing import List, Optional
from utils.market_data import (
    INFLACIYA_GOD,
    PAZARNO_POSKAPVANE_GOD,
    get_progres_koef,
    get_meseci_do_akt16,
)


def badeshta_cena(
    pokupna: float,
    etap: str,
    godini: float,
    inflaciya: Optional[float] = None,
    pazarno_poskapvane: Optional[float] = None,
) -> float:
    """
    Изчислява очакваната бъдеща стойност на имота.

    pokupna           — покупна цена в €
    etap              — строителен етап (ключ от PROGRES_KOEFICIENTI)
    godini            — хоризонт в години
    inflaciya         — годишна инфлация (None → пазарна стойност)
    pazarno_poskapvane — годишен пазарен ръст (None → пазарна стойност)
    """
    inf = inflaciya if inflaciya is not None else INFLACIYA_GOD
    paz = pazarno_poskapvane if pazarno_poskapvane is not None else PAZARNO_POSKAPVANE_GOD
    progres = get_progres_koef(etap)

    return pokupna * ((1 + inf) ** godini) * ((1 + paz) ** godini) * progres


def badeshta_cena_po_godini(
    pokupna: float,
    etap: str,
    max_godini: int = 10,
    inflaciya: Optional[float] = None,
    pazarno_poskapvane: Optional[float] = None,
) -> List[float]:
    """Връща списък с очакваната стойност за всяка година от 0 до max_godini."""
    return [
        badeshta_cena(pokupna, etap, g, inflaciya, pazarno_poskapvane)
        for g in range(max_godini + 1)
    ]


def kapital_pechalba(
    pokupna: float,
    etap: str,
    godini: float,
    notarialni_pct: float = 0.03,
    prodajbeni_razkhodi_pct: float = 0.025,
    inflaciya: Optional[float] = None,
    pazarno_poskapvane: Optional[float] = None,
) -> dict:
    """
    Изчислява капиталовата печалба при продажба.
    Връща речник с всички ключови метрики.
    """
    badezhta = badeshta_cena(pokupna, etap, godini, inflaciya, pazarno_poskapvane)
    razkhodi_pokupka = pokupna * notarialni_pct
    razkhodi_prodajba = badezhta * prodajbeni_razkhodi_pct
    brutna_pechalba = badezhta - pokupna - razkhodi_pokupka - razkhodi_prodajba
    roi_pct = (brutna_pechalba / (pokupna + razkhodi_pokupka)) * 100 if pokupna > 0 else 0.0
    godishen_roi = ((1 + roi_pct / 100) ** (1 / max(godini, 0.001)) - 1) * 100 if godini > 0 else 0.0

    return {
        "pokupna_cena": pokupna,
        "badeshta_cena": badezhta,
        "razkhodi_pokupka": razkhodi_pokupka,
        "razkhodi_prodajba": razkhodi_prodajba,
        "brutna_pechalba": brutna_pechalba,
        "roi_pct": roi_pct,
        "godishen_roi": godishen_roi,
        "godini": godini,
    }


def meseci_do_akt16(etap: str) -> int:
    """Месеци до Акт 16 от текущия строителен етап."""
    return get_meseci_do_akt16(etap)
