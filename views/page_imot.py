"""Страница 3 — Оценка на имот."""
from __future__ import annotations
import streamlit as st
from utils.locations import (
    get_all_cities, get_zones, get_avg_price, get_avg_rent,
    get_imotbg_url, get_zone_type,
)
from utils.market_data import (
    TIPOVE_STROITELSTVO, PROGRES_KOEFICIENTI,
    LIHVA_DEFAULT, NOTARIALNI_PCT,
    STROITELSTVO_KOEF, STROITELSTVO_OPIS,
)
from utils.styles import format_eur, format_pct, section_label
from utils.calculations import mesechna_vnоska

ALL_CITIES = get_all_cities()

ETAPI = list(PROGRES_KOEFICIENTI.keys())

IZLOZHENIYA = ["Юг", "Югоизток", "Югозапад", "Изток", "Запад", "Север", "Смесено"]

# Вид имот — типични площи и imot.bg slugове
VID_IMOT_DATA = {
    "1-стаен":       {"sqm": 40,  "slug": "ednostaen"},
    "2-стаен":       {"sqm": 65,  "slug": "dvustaen"},
    "3-стаен":       {"sqm": 85,  "slug": "tristaen"},
    "4-стаен":       {"sqm": 110, "slug": "chetiristaen"},
    "Мезонет":       {"sqm": 130, "slug": "mezonet"},
    "Ателие/Студио": {"sqm": 35,  "slug": "atelie-tavan"},
    "Къща":          {"sqm": 150, "slug": "kashta"},
}
VID_IMOT_OPTIONS = list(VID_IMOT_DATA.keys())

RELEVANTEN_REMONT = [
    "На зелено (след разрешение)",
    "Акт 14 (груб строеж)",
    "Акт 15 (техническа приемка)",
    "Готов стар — за ремонт",
    "Готов стар — шпакловка и замазка",
]

# Цветове за тип зона
ZONE_TYPE_COLORS = {
    "luxury":   "#a78bfa",
    "premium":  "#c9a84c",
    "mid_high": "#63b3ed",
    "mid":      "#9ca3af",
    "economy":  "#f6ad55",
    "suburb":   "#68d391",
}
ZONE_TYPE_LABELS = {
    "luxury":   "Луксозна",
    "premium":  "Премиум",
    "mid_high": "Добър сегмент",
    "mid":      "Масов сегмент",
    "economy":  "Достъпен",
    "suburb":   "Покрайнини",
}


def render():
    im = st.session_state.imot

    st.markdown('<p class="page-indicator">СТЪПКА 2</p>', unsafe_allow_html=True)
    st.markdown("# 🏗️ Оценка на имот")
    st.markdown(
        '<p style="color:#9ca3af">Въведи параметрите на имота — автоматично получаваш '
        'пазарна справка и входни данни за 7-те стратегии.</p>',
        unsafe_allow_html=True,
    )

    # ═══════════════════════════════════════════════════════════════════════
    # СЕКЦИЯ А — ВХОДНИ ДАННИ
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(section_label("А. Данни за имота"), unsafe_allow_html=True)

    # ── ВИД НА ИМОТА ──────────────────────────────────────────────────────
    current_vid = im.get("vid_imot", "2-стаен")
    if current_vid not in VID_IMOT_OPTIONS:
        current_vid = "2-стаен"
    new_vid = st.selectbox(
        "Вид на имота",
        VID_IMOT_OPTIONS,
        index=VID_IMOT_OPTIONS.index(current_vid),
    )
    # Ако се сменя вида — актуализира типичната площ
    if new_vid != im.get("vid_imot"):
        im["vid_imot"] = new_vid
        im["kvadraturi"] = float(VID_IMOT_DATA[new_vid]["sqm"])
    im["vid_imot"] = new_vid

    col1, col2 = st.columns(2)

    with col1:
        im["cena"] = st.number_input(
            "Покупна цена (€)",
            min_value=1000.0, max_value=5_000_000.0, step=1000.0,
            value=float(im["cena"]),
        )
        im["kvadraturi"] = st.number_input(
            "Квадратура (кв.м)",
            min_value=10.0, max_value=1000.0, step=1.0,
            value=float(im["kvadraturi"]),
        )

        cena_kvm = im["cena"] / im["kvadraturi"] if im["kvadraturi"] > 0 else 0
        st.markdown(
            f'<p style="color:#c9a84c;font-size:0.9rem">⚡ Цена/кв.м: '
            f'<strong>{format_eur(cena_kvm)}</strong></p>',
            unsafe_allow_html=True,
        )

        # ── ГРАД + КВАРТАЛ ─────────────────────────────────────────────
        grad_idx = ALL_CITIES.index(im["grad"]) if im["grad"] in ALL_CITIES else 0
        im["grad"] = st.selectbox("Град", ALL_CITIES, index=grad_idx)

        zones_for_city = get_zones(im["grad"])
        # Ако текущата zona не е валидна за новия град — reset
        if im.get("zona") not in zones_for_city:
            im["zona"] = zones_for_city[0]

        zona_idx = zones_for_city.index(im["zona"])
        im["zona"] = st.selectbox("Квартал / Район", zones_for_city, index=zona_idx)

        # Тип на зоната — badge
        zone_t = get_zone_type(im["grad"], im["zona"])
        zone_color = ZONE_TYPE_COLORS.get(zone_t, "#9ca3af")
        zone_label = ZONE_TYPE_LABELS.get(zone_t, zone_t)
        st.markdown(
            f'<span style="background:{zone_color}22;color:{zone_color};'
            f'border:1px solid {zone_color}44;border-radius:4px;'
            f'padding:2px 8px;font-size:0.75rem;font-weight:600">'
            f'{zone_label}</span>',
            unsafe_allow_html=True,
        )

    with col2:
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            im["etaj"] = st.number_input(
                "Етаж", min_value=0, max_value=100, step=1, value=int(im["etaj"])
            )
        with col_e2:
            im["obshto_etaji"] = st.number_input(
                "Общо етажи", min_value=1, max_value=100, step=1,
                value=int(im["obshto_etaji"])
            )

        im["izlozhenie"] = st.selectbox(
            "Изложение",
            IZLOZHENIYA,
            index=IZLOZHENIYA.index(im["izlozhenie"]) if im["izlozhenie"] in IZLOZHENIYA else 0,
        )
        im["tip_stroitelstvo"] = st.selectbox(
            "Тип строителство",
            TIPOVE_STROITELSTVO,
            index=TIPOVE_STROITELSTVO.index(im["tip_stroitelstvo"])
            if im["tip_stroitelstvo"] in TIPOVE_STROITELSTVO else 0,
        )
        im["etap"] = st.selectbox(
            "Текущо състояние",
            ETAPI,
            index=ETAPI.index(im["etap"]) if im["etap"] in ETAPI else 4,
        )

    # ── НАЕМ + РЕМОНТ ─────────────────────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        pazar_naem = get_avg_rent(im["grad"], im["zona"], im["kvadraturi"])
        current_naem = float(im.get("ochakvаn_naem", 0))
        im["ochakvаn_naem"] = st.number_input(
            "Очакван месечен наем (€)",
            min_value=0.0, max_value=20000.0, step=25.0,
            value=current_naem,
            help=(
                f"Въведи реалистичен наем на база собствено проучване. "
                f"Пазарна ориентировъчна стойност: ~{format_eur(pazar_naem)}/мес "
                f"за {im['grad']} / {im['zona']}."
            ),
        )
        if im["ochakvаn_naem"] == 0:
            st.warning("⚠️ Въведи очакван месечен наем за по-точна калкулация.")
        else:
            st.caption(f"Пазарна справка: ~{format_eur(pazar_naem)}/мес")

    with col2:
        if im["etap"] in RELEVANTEN_REMONT:
            im["remont_byudzhet"] = st.number_input(
                "Бюджет за ремонт (€)",
                min_value=0.0, max_value=500000.0, step=500.0,
                value=float(im["remont_byudzhet"]),
            )
        else:
            im["remont_byudzhet"] = 0.0
            st.info("Ремонт не е необходим при текущото състояние.")

    # ═══════════════════════════════════════════════════════════════════════
    # СЕКЦИЯ Б — ФИНАНСИРАНЕ
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown(section_label("Б. Финансиране"), unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        im["samoychastie_pct"] = st.slider(
            "Самоучастие (%)",
            min_value=10, max_value=100, step=5,
            value=int(im["samoychastie_pct"] * 100),
        ) / 100.0
        samoych_eur = im["cena"] * im["samoychastie_pct"]
        kredit_eur  = im["cena"] * (1 - im["samoychastie_pct"])
        st.caption(f"Самоучастие: {format_eur(samoych_eur)} | Кредит: {format_eur(kredit_eur)}")

    with col2:
        im["lihva"] = st.number_input(
            "Лихва (%/год.)",
            min_value=0.1, max_value=20.0, step=0.1,
            value=float(im["lihva"] * 100),
            help="Средна пазарна лихва за 2026: ~2.5%",
        ) / 100.0
        im["srok_god"] = st.number_input(
            "Срок (години)",
            min_value=5, max_value=35, step=1,
            value=int(im["srok_god"]),
        )

    with col3:
        im["notarialni_pct"] = st.slider(
            "Нотариални такси и разходи (%)",
            min_value=2, max_value=8, step=1,
            value=int(im["notarialni_pct"] * 100),
            help="Данък придобиване + нотариус + вписване + адвокат. Типично 3-5%.",
        ) / 100.0
        notarialni_eur = im["cena"] * im["notarialni_pct"]
        vnоska = mesechna_vnоska(kredit_eur, im["lihva"], im["srok_god"])
        st.caption(f"Такси: {format_eur(notarialni_eur)} | Вноска: {format_eur(vnоska)}/мес")

    st.session_state.imot = im

    # ═══════════════════════════════════════════════════════════════════════
    # СЕКЦИЯ В — ПАЗАРНА СПРАВКА ПО КВАРТАЛ
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown(section_label("В. Пазарна справка"), unsafe_allow_html=True)

    # Пазарната средна се коригира по тип строителство
    pazarna_baza     = get_avg_price(im["grad"], im["zona"])
    str_koef         = STROITELSTVO_KOEF.get(im["tip_stroitelstvo"], 1.0)
    pazarna_sredna   = round(pazarna_baza * str_koef)
    razlika_pct      = ((cena_kvm - pazarna_sredna) / pazarna_sredna * 100) if pazarna_sredna > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Цена/кв.м на имота", format_eur(cena_kvm))
    with col2:
        koef_label = "" if str_koef == 1.0 else f" × {str_koef}"
        st.metric(
            f"Пазарна ({im['zona']}{koef_label})",
            format_eur(pazarna_sredna),
            help=(
                f"Базова средна за квартала: {format_eur(pazarna_baza)}/кв.м  \n"
                f"Корекция за '{im['tip_stroitelstvo']}': × {str_koef}  \n"
                f"Изт.: BulgarianProperties, SafeNews, Profit.bg Q1 2026"
            ),
        )
    with col3:
        st.metric(
            "Разлика от пазара",
            format_pct(razlika_pct),
            delta=format_eur(cena_kvm - pazarna_sredna),
        )

    # Описание на типа строителство
    str_opis = STROITELSTVO_OPIS.get(im["tip_stroitelstvo"], "")
    if str_opis:
        st.caption(f"🏗️ {im['tip_stroitelstvo']}: {str_opis}")

    # Traffic light
    if razlika_pct <= -10:
        indik, indik_text, indik_color = (
            "🟢",
            f"Под пазара с {abs(razlika_pct):.1f}% — ДОБРА СДЕЛКА",
            "#48bb78",
        )
    elif razlika_pct >= 10:
        indik, indik_text, indik_color = (
            "🔴",
            f"Над пазара с {razlika_pct:.1f}% — СКЪП ИМОТ",
            "#fc8181",
        )
    else:
        indik, indik_text, indik_color = (
            "🟡",
            f"На пазарната цена (±{abs(razlika_pct):.1f}%)",
            "#f6e05e",
        )

    st.markdown(
        f"""
        <div class="rm-card" style="border-left:4px solid {indik_color};padding:1rem 1.5rem">
            <span style="font-size:1.5rem">{indik}</span>
            <strong style="color:{indik_color};margin-left:0.5rem">{indik_text}</strong>
            <p style="color:#6b7280;font-size:0.78rem;margin:0.3rem 0 0 2rem">
                Пазарна средна за <strong style="color:#e8eaf0">{im['zona']}</strong>
                ({im['grad']}, {im['tip_stroitelstvo']}) — {format_eur(pazarna_sredna)}/кв.м
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── IMOT.BG БУТОН ─────────────────────────────────────────────────────
    sqm_min = max(10, int(im["kvadraturi"]) - 10)
    sqm_max = int(im["kvadraturi"]) + 10
    price_min = int(im["cena"] * 0.85)
    price_max = int(im["cena"] * 1.15)

    vid = im.get("vid_imot", "2-стаен")
    room_slug = VID_IMOT_DATA.get(vid, {}).get("slug", "dvustaen")

    # Градски slug за imot.bg
    from utils.locations import _CITY_SLUGS, _SOFIA_ZONE_SLUGS
    city_slug = _CITY_SLUGS.get(im["grad"], "grad-sofiya")
    zone_slug = ""
    if im["grad"] == "София":
        z = _SOFIA_ZONE_SLUGS.get(im["zona"])
        if z:
            zone_slug = f"/{z}"

    imot_url = (
        f"https://www.imot.bg/obiavi/prodazhbi/{city_slug}{zone_slug}/{room_slug}/"
    )

    st.markdown(
        f'<a href="{imot_url}" target="_blank" style="text-decoration:none">'
        f'<div class="rm-card" style="cursor:pointer;padding:0.75rem 1.25rem;'
        f'display:flex;align-items:center;gap:0.75rem">'
        f'<span style="font-size:1.3rem">🔍</span>'
        f'<div>'
        f'<strong style="color:#e8eaf0">Виж подобни имоти в imot.bg</strong><br>'
        f'<span style="color:#9ca3af;font-size:0.78rem">'
        f'{vid} · {im["grad"]}'
        f'{" · " + im["zona"] if zone_slug else ""}'
        f' · {sqm_min}–{sqm_max} кв.м'
        f'</span>'
        f'</div>'
        f'<span style="margin-left:auto;color:#c9a84c;font-size:0.8rem">↗ нов таб</span>'
        f'</div></a>',
        unsafe_allow_html=True,
    )

    # ═══════════════════════════════════════════════════════════════════════
    # ОБОБЩЕНИЕ
    # ═══════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown(section_label("📋 Обобщение на имота"), unsafe_allow_html=True)

    r1, r2, r3, r4, r5 = st.columns(5)
    with r1:
        st.metric("Покупна цена", format_eur(im["cena"]))
    with r2:
        st.metric("Самоучастие", format_eur(samoych_eur))
    with r3:
        st.metric("Нотариални такси", format_eur(notarialni_eur))
    with r4:
        remont = im["remont_byudzhet"] if im["etap"] in RELEVANTEN_REMONT else 0.0
        st.metric("Ремонт", format_eur(remont))
    with r5:
        total = samoych_eur + notarialni_eur + remont
        st.metric("Общо вложение", format_eur(total))

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("📊  Виж 7-те стратегии", type="primary", use_container_width=True):
            st.session_state.page = "strategii"
            st.rerun()
