"""
Препоръчителна логика — коя стратегия е най-подходяща за даден профил.
"""
from __future__ import annotations
from typing import Dict, Any, Optional


def preporycha_strategia(
    risk_tolerans: str,
    investicionen_horiont: str,
    svoboden_cash: float,
    mesecen_cash_flow_nujda: float,
    etap: str,
    max_imot: float,
) -> Dict[str, Any]:
    """
    Препоръчва оптималната стратегия на база профила на инвеститора.

    risk_tolerans: "Нисък" | "Среден" | "Висок"
    investicionen_horiont: "Краткосрочен (1-3 год.)" | "Средносрочен (3-7 год.)" | "Дългосрочен (7+ год.)"
    svoboden_cash: наличен кеш в €
    mesecen_cash_flow_nujda: нужда от месечен паричен поток (0 = не е нужен)
    etap: строителен етап на имота
    max_imot: максимален имот по кредитен капацитет
    """

    preporyka = {}
    vsichki_strategii = []

    # Оценка по рисков толеранс
    risk_skor = {"Нисък": 1, "Среден": 2, "Висок": 3}.get(risk_tolerans, 2)

    # Оценка по хоризонт
    hor_skor = {
        "Краткосрочен (1-3 год.)": 1,
        "Средносрочен (3-7 год.)": 2,
        "Дългосрочен (7+ год.)": 3,
    }.get(investicionen_horiont, 2)

    # Строителни стратегии (1, 2, 3)
    if etap in ["Преди разрешение за строеж", "На зелено (след разрешение)", "Акт 14 (груб строеж)", "Акт 15 (техническа приемка)"]:
        if risk_skor >= 2 and hor_skor >= 2:
            vsichki_strategii.append({
                "id": "zeleno",
                "ime": "Покупка на зелено / в строеж",
                "skor": risk_skor + hor_skor + (1 if etap != "Преди разрешение за строеж" else 0),
                "pricina": "Имотът е в строеж — можеш да спечелиш от прогреса на строителството.",
            })

    # Стратегия наем (4)
    if mesecen_cash_flow_nujda > 0 or hor_skor >= 2:
        cf_skor = 3 if mesecen_cash_flow_nujda > 0 else 2
        vsichki_strategii.append({
            "id": "naem",
            "ime": "Покупка с цел отдаване под наем",
            "skor": cf_skor + (3 - risk_skor),
            "pricina": "Генерира стабилен месечен паричен поток с нисък риск.",
        })

    # Fix & Flip (5)
    if risk_skor >= 2 and hor_skor == 1 and svoboden_cash >= 10000:
        vsichki_strategii.append({
            "id": "fix_flip",
            "ime": "Fix & Flip",
            "skor": risk_skor + 1,
            "pricina": "Краткосрочна стратегия с висок ROI при наличен кеш за ремонт.",
        })

    # Buy & Hold (6)
    if hor_skor >= 2:
        vsichki_strategii.append({
            "id": "buy_hold",
            "ime": "Buy & Hold (задържане 5-10 год.)",
            "skor": hor_skor + (3 - risk_skor) + 1,
            "pricina": "Оптимална дългосрочна стратегия за натрупване на капитал.",
        })

    # Ново строителство готов (7)
    if risk_skor == 1 or hor_skor >= 2:
        vsichki_strategii.append({
            "id": "novo_gotov",
            "ime": "Ново строителство — готов имот",
            "skor": (3 - risk_skor) + hor_skor,
            "pricina": "Нисък риск, нов имот с гаранция, готов за наем веднага.",
        })

    # Сортиране по сkor
    vsichki_strategii.sort(key=lambda x: x["skor"], reverse=True)

    najdobra = vsichki_strategii[0] if vsichki_strategii else None

    return {
        "najdobra_strategia": najdobra,
        "vsichki_strategii": vsichki_strategii,
        "risk_tolerans": risk_tolerans,
        "horiont": investicionen_horiont,
    }


def profil_preporyaka_tekst(
    risk_tolerans: str,
    investicionen_horiont: str,
    svoboden_cash: float,
    mesecen_cash_flow: float,
) -> str:
    """Генерира текстова персонална препоръка."""
    lines = []

    if risk_tolerans == "Нисък":
        lines.append("Профилът ти е **консервативен** — фокусирай се върху стабилни имоти с предвидим наем.")
    elif risk_tolerans == "Среден":
        lines.append("Профилът ти е **балансиран** — можеш да комбинираш наем и строителство в начален етап.")
    else:
        lines.append("Профилът ти е **агресивен** — имаш капацитет за по-рискови стратегии с висок ROI.")

    if investicionen_horiont == "Краткосрочен (1-3 год.)":
        lines.append("Кратък хоризонт → Fix & Flip или покупка на Акт 14/15 и бърза препродажба.")
    elif investicionen_horiont == "Средносрочен (3-7 год.)":
        lines.append("Среден хоризонт → Покупка на зелено + наем при завършване е оптимална комбинация.")
    else:
        lines.append("Дълъг хоризонт → Buy & Hold е царят — имотът расте, наемите се натрупват.")

    if mesecen_cash_flow > 0:
        lines.append(f"Нуждаеш се от **€{mesecen_cash_flow:.0f}/мес** паричен поток → приоритизирай наемни имоти.")

    if svoboden_cash < 15000:
        lines.append("**Внимание:** Ограничен кеш — помисли за партньорство или старт с по-малък имот.")
    elif svoboden_cash > 50000:
        lines.append("Разполагаш с добра кешова позиция — можеш да действаш бързо при добра оферта.")

    return "\n\n".join(lines)


def risk_badge(risk: str) -> str:
    """Връща HTML badge за риска."""
    colors = {
        "Много висок": "#e53e3e",
        "Висок": "#ed8936",
        "Среден": "#ecc94b",
        "Нисък-Среден": "#48bb78",
        "Нисък": "#38a169",
    }
    color = colors.get(risk, "#718096")
    return f'<span style="background:{color};color:white;padding:2px 8px;border-radius:4px;font-size:0.8em">{risk}</span>'
