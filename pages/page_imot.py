"""Страница 3 — Оценка на имот."""
from __future__ import annotations
import streamlit as st
from utils.market_data import (
    GRADOVE, ZONI, TIPOVE_STROITELSTVO, PROGRES_KOEFICIENTI,
    LIHVA_DEFAULT, NAEMI_DVUSTAEN,
    get_pazarna_cena, get_sreden_naem,
    NOTARIALNI_PCT,
)
from utils.styles import format_eur, format_pct
from utils.calculations import mesechna_vnоska


ETAPI = list(PROGRES_KOEFICIENTI.keys())

IZLOZHENIYA = ["Юг", "Югоизток", "Югозапад", "Изток", "Запад", "Север", "Смесено"]

RELEVANTEN_REMONT = [
    "На зелено (след разрешение)",
    "Акт 14 (груб строеж)",
    "Акт 15 (техническа приемка)",
    "Готов стар — за ремонт",
    "Готов стар — шпакловка и замазка",
]


def render():
    im = st.session_state.imot

    st.markdown('<p class="page-indicator">СТЪПКА 2</p>', unsafe_allow_html=True)
    st.markdown("# 🏗️ Оценка на имот")
    st.markdown(
        '<p style="color:#9ca3af">Въведи параметрите на имота — автоматично получаваш пазарна справка и входни данни за 7-те стратегии.</p>',
        unsafe_allow_html=True,
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # СЕКЦИЯ А — ВХОДНИ ДАННИ
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### А. Данни за имота")

    col1, col2 = st.columns(2)

    with col1:
        im["cena"] = st.number_input(
            "Покупна цена (€)",
            min_value=1000.0, max_value=5000000.0, step=1000.0,
            value=float(im["cena"]),
        )
        im["kvadraturi"] = st.number_input(
            "Квадратура (кв.м)",
            min_value=10.0, max_value=1000.0, step=1.0,
            value=float(im["kvadraturi"]),
        )

        # Авто: цена/кв.м
        cena_kvm = im["cena"] / im["kvadraturi"] if im["kvadraturi"] > 0 else 0
        st.markdown(
            f'<p style="color:#c9a84c;font-size:0.9rem">⚡ Цена/кв.м: <strong>{format_eur(cena_kvm)}</strong></p>',
            unsafe_allow_html=True,
        )

        im["grad"] = st.selectbox(
            "Град",
            GRADOVE,
            index=GRADOVE.index(im["grad"]) if im["grad"] in GRADOVE else 0,
        )
        im["zona"] = st.selectbox(
            "Зона",
            ZONI,
            index=ZONI.index(im["zona"]) if im["zona"] in ZONI else 1,
        )

    with col2:
        col_e1, col_e2 = st.columns(2)
        with col_e1:
            im["etaj"] = st.number_input("Етаж", min_value=0, max_value=100, step=1, value=int(im["etaj"]))
        with col_e2:
            im["obshto_etaji"] = st.number_input("Общо етажи", min_value=1, max_value=100, step=1, value=int(im["obshto_etaji"]))

        im["izlozhenie"] = st.selectbox(
            "Изложение",
            IZLOZHENIYA,
            index=IZLOZHENIYA.index(im["izlozhenie"]) if im["izlozhenie"] in IZLOZHENIYA else 0,
        )
        im["tip_stroitelstvo"] = st.selectbox(
            "Тип строителство",
            TIPOVE_STROITELSTVO,
            index=TIPOVE_STROITELSTVO.index(im["tip_stroitelstvo"]) if im["tip_stroitelstvo"] in TIPOVE_STROITELSTVO else 0,
        )
        im["etap"] = st.selectbox(
            "Текущо състояние",
            ETAPI,
            index=ETAPI.index(im["etap"]) if im["etap"] in ETAPI else 4,
        )

    # Очакван наем (авто от пазарни данни)
    col1, col2 = st.columns(2)
    with col1:
        pazar_naem = get_sreden_naem(im["grad"], im["zona"], im["kvadraturi"])
        im["ochakvаn_naem"] = st.number_input(
            "Очакван месечен наем (€)",
            min_value=0.0, max_value=20000.0, step=25.0,
            value=float(im["ochakvаn_naem"]) if im["ochakvаn_naem"] > 0 else float(pazar_naem),
            help=f"Пазарна референция: ~{format_eur(pazar_naem)}/мес за {im['grad']} / {im['zona']}",
        )
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

    # ═══════════════════════════════════════════════════════════════════════════
    # СЕКЦИЯ Б — ФИНАНСИРАНЕ
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("### Б. Финансиране")

    col1, col2, col3 = st.columns(3)
    with col1:
        im["samoychastie_pct"] = st.slider(
            "Самоучастие (%)",
            min_value=10, max_value=100, step=5,
            value=int(im["samoychastie_pct"] * 100),
        ) / 100.0
        samoych_eur = im["cena"] * im["samoychastie_pct"]
        kredit_eur = im["cena"] * (1 - im["samoychastie_pct"])
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

    # ═══════════════════════════════════════════════════════════════════════════
    # СЕКЦИЯ В — ПАЗАРНА СПРАВКА
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### В. Пазарна справка")

    pazarna_sredna = get_pazarna_cena(im["grad"], im["zona"])
    razlika_pct = ((cena_kvm - pazarna_sredna) / pazarna_sredna * 100) if pazarna_sredna > 0 else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Цена/кв.м на имота", format_eur(cena_kvm))
    with col2:
        st.metric(f"Пазарна средна ({im['grad']} / {im['zona']})", format_eur(pazarna_sredna))
    with col3:
        st.metric("Разлика от пазара", format_pct(razlika_pct), delta=format_eur(cena_kvm - pazarna_sredna))

    # Traffic light индикатор
    if razlika_pct <= -10:
        indik = "🟢"
        indik_text = f"Под пазара с {abs(razlika_pct):.1f}% — ДОБРА СДЕЛКА"
        indik_color = "#48bb78"
    elif razlika_pct >= 10:
        indik = "🔴"
        indik_text = f"Над пазара с {razlika_pct:.1f}% — СКЪП ИМОТ"
        indik_color = "#fc8181"
    else:
        indik = "🟡"
        indik_text = f"На пазарната цена (±{abs(razlika_pct):.1f}%)"
        indik_color = "#f6e05e"

    st.markdown(
        f"""
        <div class="rm-card" style="border-left:4px solid {indik_color};padding:1rem 1.5rem">
            <span style="font-size:1.5rem">{indik}</span>
            <strong style="color:{indik_color};margin-left:0.5rem">{indik_text}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Бутон към imot.bg
    plosha_min = max(10, int(im["kvadraturi"]) - 10)
    plosha_max = int(im["kvadraturi"]) + 10
    cena_min = int(im["cena"] * 0.85)
    cena_max = int(im["cena"] * 1.15)

    grad_map = {"София": "sofia", "Варна": "varna", "Пловдив": "plovdiv", "Бургас": "burgas", "Стара Загора": "stara-zagora"}
    grad_slug = grad_map.get(im["grad"], "sofia")

    imot_url = (
        f"https://www.imot.bg/pcgi/imot.cgi?act=11&f1={grad_slug}"
        f"&f4={plosha_min}&f5={plosha_max}&f8={cena_min}&f9={cena_max}&f0=0"
    )

    st.markdown(
        f'<a href="{imot_url}" target="_blank" style="text-decoration:none">'
        f'<div class="rm-card" style="cursor:pointer;text-align:center;padding:0.75rem">'
        f'🔍 <strong>Виж подобни имоти в imot.bg</strong> '
        f'<span style="color:#9ca3af;font-size:0.8rem">({im["grad"]}, {plosha_min}–{plosha_max} кв.м, {format_eur(cena_min)}–{format_eur(cena_max)})</span>'
        f'</div></a>',
        unsafe_allow_html=True,
    )

    # ═══════════════════════════════════════════════════════════════════════════
    # ОБОБЩЕНИЕ
    # ═══════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 📋 Обобщение на имота")

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
