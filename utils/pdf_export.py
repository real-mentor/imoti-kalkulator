"""
PDF генератор — брандиран инвестиционен анализ за Real Mentor.
Използва ReportLab. DejaVu Sans (bundled) → пълна поддръжка на кирилица.
"""
from __future__ import annotations

import os
from datetime import date
from io import BytesIO
from typing import Any, Dict, List, Optional

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ─── Шрифтове ────────────────────────────────────────────────────────────────

_FONTS_DIR = os.path.join(os.path.dirname(__file__), "..", "fonts")
_REG_PATH  = os.path.join(_FONTS_DIR, "DejaVuSans.ttf")
_BOLD_PATH = os.path.join(_FONTS_DIR, "DejaVuSans-Bold.ttf")

_FONT_REGISTERED = False


def _register_fonts() -> None:
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("DejaVu",     _REG_PATH))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", _BOLD_PATH))
    pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold",
                                  italic="DejaVu", boldItalic="DejaVu-Bold")
    _FONT_REGISTERED = True


# ─── Цветова палитра ─────────────────────────────────────────────────────────

NAVY   = colors.HexColor("#1E3A5F")
DARK   = colors.HexColor("#2C3E50")
GOLD   = colors.HexColor("#C9A84C")
GREEN  = colors.HexColor("#27AE60")
RED    = colors.HexColor("#E74C3C")
GRAY   = colors.HexColor("#7F8C8D")
LGRAY  = colors.HexColor("#ECF0F1")
WHITE  = colors.white

PAGE_W, PAGE_H = A4


# ─── Стилове ─────────────────────────────────────────────────────────────────

def _styles() -> Dict[str, ParagraphStyle]:
    return {
        "title": ParagraphStyle("title", fontName="DejaVu-Bold", fontSize=28,
                                textColor=NAVY, spaceAfter=6, leading=34),
        "subtitle": ParagraphStyle("subtitle", fontName="DejaVu", fontSize=14,
                                   textColor=GOLD, spaceAfter=4),
        "h1": ParagraphStyle("h1", fontName="DejaVu-Bold", fontSize=16,
                              textColor=NAVY, spaceBefore=12, spaceAfter=6, leading=20),
        "h2": ParagraphStyle("h2", fontName="DejaVu-Bold", fontSize=12,
                              textColor=NAVY, spaceBefore=8, spaceAfter=4),
        "body": ParagraphStyle("body", fontName="DejaVu", fontSize=10,
                               textColor=DARK, leading=15, spaceAfter=4),
        "small": ParagraphStyle("small", fontName="DejaVu", fontSize=8,
                                textColor=GRAY, leading=12),
        "accent": ParagraphStyle("accent", fontName="DejaVu-Bold", fontSize=22,
                                 textColor=GOLD, spaceAfter=4),
        "green": ParagraphStyle("green", fontName="DejaVu-Bold", fontSize=10,
                                textColor=GREEN),
        "red":   ParagraphStyle("red",   fontName="DejaVu-Bold", fontSize=10,
                                textColor=RED),
        "label": ParagraphStyle("label", fontName="DejaVu", fontSize=8,
                                textColor=GRAY, spaceAfter=0),
        "header_small": ParagraphStyle("header_small", fontName="DejaVu", fontSize=8,
                                       textColor=GRAY),
        "footer_text": ParagraphStyle("footer_text", fontName="DejaVu", fontSize=8,
                                      textColor=GRAY, alignment=1),
        "cta_title": ParagraphStyle("cta_title", fontName="DejaVu-Bold", fontSize=13,
                                    textColor=NAVY, spaceBefore=6, spaceAfter=4),
        "step": ParagraphStyle("step", fontName="DejaVu", fontSize=10,
                               textColor=DARK, leading=15, leftIndent=12, spaceAfter=5),
    }


# ─── Номерация + Header ───────────────────────────────────────────────────────

class _PageNumCanvas:
    """Добавя header и номерация след корицата чрез platypus canvas callback."""

    def __init__(self, total_pages: int):
        self.total = total_pages

    def __call__(self, canvas, doc):
        page = doc.page
        w, h = PAGE_W, PAGE_H
        canvas.saveState()

        if page > 1:
            # Тънка линия горе
            canvas.setStrokeColor(GOLD)
            canvas.setLineWidth(0.5)
            canvas.line(2 * cm, h - 1.5 * cm, w - 2 * cm, h - 1.5 * cm)
            # Лого текст горе вляво
            canvas.setFont("DejaVu", 8)
            canvas.setFillColor(GRAY)
            canvas.drawString(2 * cm, h - 1.2 * cm, "Real Mentor — Инвестиционен Анализ")

        # Страница X от Y долу вдясно
        canvas.setFont("DejaVu", 8)
        canvas.setFillColor(GRAY)
        canvas.drawRightString(w - 2 * cm, 1.2 * cm,
                               f"Страница {page} от {self.total}")

        canvas.restoreState()


# ─── Помощни функции ─────────────────────────────────────────────────────────

def _eur(v: float) -> str:
    return f"€{v:,.0f}"


def _pct(v: float) -> str:
    return f"{v:.1f}%"


def _gold_line() -> HRFlowable:
    return HRFlowable(width="100%", thickness=1.5, color=GOLD, spaceAfter=8)


def _thin_line() -> HRFlowable:
    return HRFlowable(width="100%", thickness=0.5, color=LGRAY, spaceAfter=6)


def _table(data: List[List], col_widths: Optional[List] = None,
           header: bool = True) -> Table:
    """Таблица с брандиран дизайн."""
    if col_widths is None:
        avail = PAGE_W - 4 * cm
        col_widths = [avail / len(data[0])] * len(data[0])

    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)

    style = [
        ("FONTNAME",    (0, 0), (-1, -1), "DejaVu"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",   (0, 0), (-1, -1), DARK),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, colors.HexColor("#F8F9FA")]),
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#D5D8DC")),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]

    if header:
        style += [
            ("BACKGROUND",  (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
            ("FONTNAME",    (0, 0), (-1, 0), "DejaVu-Bold"),
            ("FONTSIZE",    (0, 0), (-1, 0), 9),
            ("LINEBELOW",   (0, 0), (-1, 0), 1.5, GOLD),
        ]

    t.setStyle(TableStyle(style))
    return t


def _kv_table(pairs: List[tuple], bold_col: bool = False) -> Table:
    """Двуколонна таблица ключ-стойност."""
    avail = PAGE_W - 4 * cm
    data = []
    for k, v in pairs:
        data.append([k, v])

    t = Table(data, colWidths=[avail * 0.55, avail * 0.45])
    style = [
        ("FONTNAME",    (0, 0), (-1, -1), "DejaVu"),
        ("FONTNAME",    (1, 0), (-1, -1), "DejaVu-Bold" if bold_col else "DejaVu"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("TEXTCOLOR",   (0, 0), (0, -1), GRAY),
        ("TEXTCOLOR",   (1, 0), (1, -1), DARK),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [WHITE, colors.HexColor("#F8F9FA")]),
        ("TOPPADDING",  (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW",   (0, 0), (-1, -1), 0.3, colors.HexColor("#E0E0E0")),
    ]
    t.setStyle(TableStyle(style))
    return t


# ─── Страница 1 — Корица ─────────────────────────────────────────────────────

def _cover(story: list, s: Dict, profil: Dict) -> None:
    email = profil.get("_email", "")

    # Голям отстъп горе
    story.append(Spacer(1, 3 * cm))

    # Лого горе вдясно — добавено чрез параграф с alignment
    logo_style = ParagraphStyle("logo", fontName="DejaVu-Bold", fontSize=11,
                                textColor=GOLD, alignment=2)
    story.append(Paragraph("Real Mentor", logo_style))
    story.append(Spacer(1, 0.5 * cm))

    story.append(_gold_line())
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Real Mentor", s["subtitle"]))
    story.append(Paragraph("Инвестиционен Анализ", s["title"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("От 0 до Първия Имот", s["subtitle"]))

    story.append(Spacer(1, 1.5 * cm))
    story.append(_gold_line())
    story.append(Spacer(1, 0.5 * cm))

    today = date.today().strftime("%d.%m.%Y")
    story.append(Paragraph(f"Дата на генериране: {today}", s["body"]))
    if email:
        story.append(Paragraph(f"Клиент: {email}", s["body"]))

    # Запълване надолу
    story.append(Spacer(1, 8 * cm))

    story.append(_thin_line())
    disclaimer = ("Този отчет е генериран автоматично от Real Mentor — Имотен Калкулатор. "
                  "Не замества професионална инвестиционна, правна или финансова консултация. "
                  "Всички изчисления са на база въведените от потребителя данни и пазарни референции за Q1 2026.")
    story.append(Paragraph(disclaimer, s["small"]))

    story.append(PageBreak())


# ─── Страница 2 — Профил ─────────────────────────────────────────────────────

def _profil_page(story: list, s: Dict, profil: Dict, kap: Dict,
                 preporyaka: Dict) -> None:
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Твоят финансов профил", s["h1"]))
    story.append(_gold_line())

    # Доходи
    story.append(Paragraph("Доходи", s["h2"]))
    story.append(_kv_table([
        ("Нетна заплата",              _eur(profil.get("neto_zaplata", 0))),
        ("Доход на партньор",          _eur(profil.get("partnyor_dohod", 0))),
        ("Допълнителни доходи",        _eur(profil.get("drugi_dohodi", 0))),
        ("Общ месечен доход",          _eur(kap.get("obshto_dohod", 0))),
    ], bold_col=True))

    story.append(Spacer(1, 0.4 * cm))

    # Разходи
    story.append(Paragraph("Разходи", s["h2"]))
    story.append(_kv_table([
        ("Месечни разходи",            _eur(profil.get("mesechni_razkhodi", 0))),
        ("Текущи кредитни вноски",     _eur(profil.get("tekushti_krediti", 0))),
        ("Свободна сума / месец",      _eur(kap.get("svobodna_suma", 0))),
        ("Макс. ипотечна вноска (40%)", _eur(kap.get("max_vnоska", 0))),
    ], bold_col=True))

    story.append(Spacer(1, 0.6 * cm))
    story.append(_thin_line())

    # Кредитен капацитет — акцент
    story.append(Paragraph("Кредитен капацитет", s["h2"]))
    story.append(_kv_table([
        ("Максимален ипотечен кредит", _eur(kap.get("max_kredit", 0))),
        ("Необходимо самоучастие",     _eur(kap.get("nujno_samoychastie", 0))),
    ]))

    story.append(Spacer(1, 0.5 * cm))

    # Потенциал — голямо число
    story.append(Paragraph("Инвестиционен потенциал", s["label"]))
    story.append(Paragraph(_eur(kap.get("max_imot", 0)), s["accent"]))
    story.append(Paragraph("максимална стойност на имот при 20% самоучастие", s["small"]))

    story.append(Spacer(1, 0.6 * cm))
    story.append(_thin_line())

    # Профил
    story.append(Paragraph("Инвестиционен профил", s["h2"]))
    story.append(_kv_table([
        ("Рисков толеранс",            profil.get("risk", "—")),
        ("Инвестиционен хоризонт",     profil.get("horiont", "—")),
        ("Целеви град",                profil.get("grad", "—")),
        ("Наличен кеш / спестявания",  _eur(profil.get("spestyavane_cash", 0))),
    ]))

    story.append(Spacer(1, 0.6 * cm))

    # Препоръчана стратегия
    naj = preporyaka.get("najdobra_strategia")
    if naj:
        story.append(Paragraph("Препоръчана стратегия", s["h2"]))
        strat_data = [
            ["Стратегия", "Причина"],
            [naj.get("ime", "—"), naj.get("pricina", "—")],
        ]
        avail = PAGE_W - 4 * cm
        t = _table(strat_data, col_widths=[avail * 0.35, avail * 0.65])
        story.append(t)

    story.append(PageBreak())


# ─── Страница 3 — Имот ───────────────────────────────────────────────────────

def _imot_page(story: list, s: Dict, im: Dict) -> None:
    from utils.locations import get_avg_price
    from utils.market_data import STROITELSTVO_KOEF

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Анализ на избрания имот", s["h1"]))
    story.append(_gold_line())

    cena       = im.get("cena", 0)
    kvm        = im.get("kvadraturi", 1)
    cena_kvm   = cena / kvm if kvm > 0 else 0
    grad       = im.get("grad", "—")
    zona       = im.get("zona", "—")
    tip_str    = im.get("tip_stroitelstvo", "Ново строителство")
    etap       = im.get("etap", "—")
    vid        = im.get("vid_imot", "—")

    story.append(Paragraph("Данни за имота", s["h2"]))
    story.append(_kv_table([
        ("Вид на имота",            vid),
        ("Покупна цена",            _eur(cena)),
        ("Квадратура",              f"{kvm:.0f} кв.м"),
        ("Цена / кв.м",             _eur(cena_kvm)),
        ("Град / Квартал",          f"{grad} / {zona}"),
        ("Тип строителство",        tip_str),
        ("Текущо състояние",        etap),
        ("Очакван месечен наем",    _eur(im.get("ochakvаn_naem", 0))),
        ("Бюджет за ремонт",        _eur(im.get("remont_byudzhet", 0))),
    ]))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Финансиране", s["h2"]))

    samoych_eur   = cena * im.get("samoychastie_pct", 0.20)
    kredit_eur    = cena * (1 - im.get("samoychastie_pct", 0.20))
    notarial_eur  = cena * im.get("notarialni_pct", 0.03)
    story.append(_kv_table([
        ("Самоучастие",             _eur(samoych_eur)),
        ("Ипотечен кредит",         _eur(kredit_eur)),
        ("Лихва",                   _pct(im.get("lihva", 0.025) * 100)),
        ("Срок",                    f"{im.get('srok_god', 25)} год."),
        ("Нотариални такси",        _eur(notarial_eur)),
    ]))

    story.append(Spacer(1, 0.5 * cm))

    # Пазарна справка
    story.append(Paragraph("Пазарна справка", s["h2"]))

    try:
        pazarna_baza   = get_avg_price(grad, zona)
        str_koef       = STROITELSTVO_KOEF.get(tip_str, 1.0)
        pazarna_sredna = round(pazarna_baza * str_koef)
        razlika_pct    = ((cena_kvm - pazarna_sredna) / pazarna_sredna * 100) if pazarna_sredna > 0 else 0

        story.append(_kv_table([
            ("Пазарна средна за квартала", _eur(pazarna_sredna) + "/кв.м"),
            ("Цена на имота",              _eur(cena_kvm) + "/кв.м"),
            ("Разлика от пазара",          _pct(razlika_pct)),
        ]))

        if razlika_pct <= -10:
            verdict = f"Под пазара с {abs(razlika_pct):.1f}% — ДОБРА СДЕЛКА"
            story.append(Paragraph(f"[OK] {verdict}", s["green"]))
        elif razlika_pct >= 10:
            verdict = f"Над пазара с {razlika_pct:.1f}% — СКЪП ИМОТ"
            story.append(Paragraph(f"[!] {verdict}", s["red"]))
        else:
            verdict = f"На пазарната цена (±{abs(razlika_pct):.1f}%)"
            story.append(Paragraph(f"[~] {verdict}", s["body"]))

    except Exception:
        story.append(Paragraph("Пазарна справка не е налична.", s["small"]))

    story.append(PageBreak())


# ─── Страница 4 — Стратегии ──────────────────────────────────────────────────

def _strategii_page(story: list, s: Dict, strategii: List[Dict],
                    najdobra: Optional[Dict]) -> None:
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Сравнение на стратегии", s["h1"]))
    story.append(_gold_line())

    avail = PAGE_W - 4 * cm
    col_w = [avail * 0.32, avail * 0.14, avail * 0.14, avail * 0.1, avail * 0.12, avail * 0.18]

    header = ["Стратегия", "Вложение", "Печалба", "ROI %", "Срок", "Риск"]
    rows = [header]

    naj_ime = najdobra.get("ime", "") if najdobra else ""

    for st in strategii:
        ime   = st.get("ime", "—")
        mark  = " *" if naj_ime and naj_ime in ime else ""
        mes   = st.get("srok_mes", 0)
        srok  = f"{mes//12}г {mes%12}м" if mes > 0 else "—"
        rows.append([
            ime + mark,
            _eur(st.get("vlozhenie", 0)),
            _eur(st.get("pechalba", 0)),
            _pct(st.get("roi_pct", 0)),
            srok,
            st.get("risk", "—"),
        ])

    t = Table(rows, colWidths=col_w, repeatRows=1)

    style = [
        ("FONTNAME",    (0, 0), (-1, -1), "DejaVu"),
        ("FONTSIZE",    (0, 0), (-1, -1), 8),
        ("TEXTCOLOR",   (0, 0), (-1, -1), DARK),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, colors.HexColor("#F8F9FA")]),
        ("GRID",        (0, 0), (-1, -1), 0.4, colors.HexColor("#D5D8DC")),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        # Header
        ("BACKGROUND",  (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR",   (0, 0), (-1, 0), WHITE),
        ("FONTNAME",    (0, 0), (-1, 0), "DejaVu-Bold"),
        ("LINEBELOW",   (0, 0), (-1, 0), 1.5, GOLD),
    ]

    # Маркирай победителя с жълт фон
    for i, st in enumerate(strategii, start=1):
        if naj_ime and naj_ime in st.get("ime", ""):
            style.append(("BACKGROUND",  (0, i), (-1, i), colors.HexColor("#FEF9E7")))
            style.append(("FONTNAME",    (0, i), (-1, i), "DejaVu-Bold"))
            style.append(("TEXTCOLOR",   (0, i), (0, i), NAVY))

    t.setStyle(TableStyle(style))
    story.append(t)

    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("* Препоръчана стратегия", s["small"]))

    if najdobra:
        story.append(Spacer(1, 0.5 * cm))
        story.append(Paragraph("Защо тази стратегия?", s["h2"]))
        story.append(Paragraph(najdobra.get("pricina", ""), s["body"]))

    story.append(PageBreak())


# ─── Страница 5 — Следващи стъпки ────────────────────────────────────────────

def _sledvashti_stapki(story: list, s: Dict, profil: Dict, kap: Dict,
                       im: Dict, najdobra: Optional[Dict]) -> None:
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("Твоите следващи стъпки", s["h1"]))
    story.append(_gold_line())

    razkhodi     = profil.get("mesechni_razkhodi", 800)
    rezerv_fond  = razkhodi * 6
    max_kredit   = kap.get("max_kredit", 0)
    spestyvane   = profil.get("spestyavane_cash", 0)
    grad         = im.get("grad", "София")
    zona         = im.get("zona", "")
    cena         = im.get("cena", 150000)
    cena_min     = round(cena * 0.85 / 1000) * 1000
    cena_max     = round(cena * 1.15 / 1000) * 1000
    naj_ime      = najdobra.get("ime", "Buy & Hold") if najdobra else "Buy & Hold"

    steps = [
        f"1.  Подготви резервен фонд от {_eur(rezerv_fond)} (6 месеца разходи) преди да влагаш капитал.",
        f"2.  Консултирай се с банка за предварително одобрение до {_eur(max_kredit)} (при твоя доход).",
        f"3.  Разгледай имоти в {grad}{' / ' + zona if zona else ''} между {_eur(cena_min)} и {_eur(cena_max)}.",
        f"4.  Използвай чеклиста за покупка в Real Mentor (7 етапа юридическа проверка).",
        f"5.  Приложи стратегия: {naj_ime} — тя съответства на твоя рисков профил и хоризонт.",
    ]

    if spestyvane < 15000:
        steps.append("6.  Обмисли партньорство или старт с по-малък имот — наличният кеш е ограничен.")
    else:
        steps.append(f"6.  Имаш {_eur(spestyvane)} кеш — можеш да действаш бързо при добра оферта.")

    steps.append("7.  Проследявай инвестицията с месечен мониторинг на паричния поток.")

    for step in steps:
        story.append(Paragraph(step, s["step"]))

    story.append(Spacer(1, 1 * cm))
    story.append(_gold_line())

    story.append(Paragraph("Готов за следващата стъпка?", s["cta_title"]))
    story.append(Paragraph(
        "Програма: От 0 до Първия Имот — realmentor.bg",
        ParagraphStyle("cta_link", fontName="DejaVu-Bold", fontSize=11, textColor=GOLD)
    ))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Real Mentor е персонализиран инструмент за инвестиционен анализ на имоти в България. "
        "Всички стратегии, калкулации и чеклисти са достъпни безплатно в приложението.",
        s["body"]
    ))


# ─── Главна функция ───────────────────────────────────────────────────────────

def generate_report(
    profil: Dict[str, Any],
    imot: Dict[str, Any],
    strategii: Optional[List[Dict]] = None,
    najdobra_strategia: Optional[Dict] = None,
    user_email: str = "",
) -> bytes:
    """
    Генерира PDF отчет и връща bytes.

    profil          — st.session_state.profil
    imot            — st.session_state.imot
    strategii       — списък с изчислени стратегии (от page_strategii)
    najdobra_strategia — препоръчаната стратегия dict
    user_email      — имейл за корицата
    """
    _register_fonts()

    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2 * cm,
        title="Real Mentor — Инвестиционен Анализ",
        author="Real Mentor",
    )

    s = _styles()
    story: List[Any] = []

    # Изчисли кредитен капацитет
    from utils.calculations import kreditен_kapacitet
    from utils.recommendation import preporycha_strategia

    kap = kreditен_kapacitet(
        neto_dohod=profil.get("neto_zaplata", 0),
        partnyor_dohod=profil.get("partnyor_dohod", 0),
        drugi_dohodi=profil.get("drugi_dohodi", 0),
        mesechni_razkhodi=profil.get("mesechni_razkhodi", 0),
        tekushti_krediti=profil.get("tekushti_krediti", 0),
        samoychastie_pct=0.20,
    )

    preporyaka = preporycha_strategia(
        risk_tolerans=profil.get("risk", "Среден"),
        investicionen_horiont=profil.get("horiont", "Средносрочен (3-7 год.)"),
        svoboden_cash=profil.get("spestyavane_cash", 0),
        mesecen_cash_flow_nujda=profil.get("target_cash_flow", 0),
        etap=imot.get("etap", "Акт 16 (готов нов)"),
        max_imot=kap.get("max_imot", 0),
    )

    naj = najdobra_strategia or preporyaka.get("najdobra_strategia")

    profil_with_email = dict(profil)
    profil_with_email["_email"] = user_email

    # Изграждане на страниците
    _cover(story, s, profil_with_email)
    _profil_page(story, s, profil_with_email, kap, preporyaka)
    _imot_page(story, s, imot)

    if strategii:
        _strategii_page(story, s, strategii, naj)

    _sledvashti_stapki(story, s, profil, kap, imot, naj)

    # Брой страници — две минавания
    _total_pages = [0]

    class _CountingCanvas:
        def __init__(self, total_ref):
            self._t = total_ref
            self._page = 0

        def __call__(self, canvas, doc):
            self._page += 1
            self._t[0] = max(self._t[0], self._page)

    counter = _CountingCanvas(_total_pages)

    # Първо минаване — брой
    buf1 = BytesIO()
    doc1 = SimpleDocTemplate(buf1, pagesize=A4,
                              leftMargin=2*cm, rightMargin=2*cm,
                              topMargin=2.2*cm, bottomMargin=2*cm)
    doc1.build(story, onFirstPage=counter, onLaterPages=counter)
    total = _total_pages[0]

    # Второ минаване — истински PDF
    story2: List[Any] = []
    _cover(story2, s, profil_with_email)
    _profil_page(story2, s, profil_with_email, kap, preporyaka)
    _imot_page(story2, s, imot)
    if strategii:
        _strategii_page(story2, s, strategii, naj)
    _sledvashti_stapki(story2, s, profil, kap, imot, naj)

    cb = _PageNumCanvas(total)
    doc.build(story2, onFirstPage=cb, onLaterPages=cb)

    return buf.getvalue()
