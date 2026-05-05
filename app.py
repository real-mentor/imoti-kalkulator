"""
Real Mentor — Калкулатор за имотни инвестиции в България
Главен файл: навигация и session state.
"""
from __future__ import annotations
import streamlit as st
from utils.styles import DARK_THEME_CSS

st.set_page_config(
    page_title="Real Mentor — Имотен Калкулатор",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(DARK_THEME_CSS, unsafe_allow_html=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────────

def init_state():
    defaults = {
        "page": "home",
        # Профил на инвеститора
        "profil": {
            "neto_zaplata": 2000.0,
            "partnyor_dohod": 0.0,
            "drugi_dohodi": 0.0,
            "mesechni_razkhodi": 800.0,
            "spestyavane_cash": 20000.0,
            "tekushti_krediti": 0.0,
            "horiont": "Средносрочен (3-7 год.)",
            "risk": "Среден",
            "grad": "София",
            "target_cash_flow": 0.0,
        },
        # Имот от Страница 3
        "imot": {
            "cena": 150000.0,
            "kvadraturi": 65.0,
            "grad": "София",
            "zona": "Средна зона",
            "etaj": 3,
            "obshto_etaji": 8,
            "izlozhenie": "Юг",
            "tip_stroitelstvo": "Ново строителство",
            "etap": "Акт 16 (готов нов)",
            "ochakvаn_naem": 650.0,
            "remont_byudzhet": 0.0,
            "samoychastie_pct": 0.20,
            "lihva": 0.025,
            "srok_god": 25,
            "notarialni_pct": 0.03,
        },
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_state()

# ─── НАВИГАЦИЯ ────────────────────────────────────────────────────────────────

PAGES = {
    "home":       ("🏠", "Начало"),
    "profil":     ("👤", "Профил"),
    "imot":       ("🏗️", "Оценка на имот"),
    "strategii":  ("📊", "Стратегии"),
    "checklist":  ("✅", "Чеклист"),
    "remont":     ("🔨", "Ремонт"),
}

with st.sidebar:
    st.markdown(
        '<p style="color:#c9a84c;font-weight:700;font-size:1.1rem;margin-bottom:0">Real Mentor</p>'
        '<p style="color:#6b7280;font-size:0.75rem;margin-top:0;margin-bottom:1.5rem">Имотен Калкулатор</p>',
        unsafe_allow_html=True,
    )

    for page_id, (icon, label) in PAGES.items():
        is_active = st.session_state.page == page_id
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{icon}  {label}", key=f"nav_{page_id}", use_container_width=True, type=btn_type):
            st.session_state.page = page_id
            st.rerun()

    st.markdown("---")
    st.markdown(
        '<p style="color:#6b7280;font-size:0.7rem;text-align:center">'
        'Real Mentor · 2026<br>'
        'Данни: Q1 2026</p>',
        unsafe_allow_html=True,
    )

# ─── ЗАРЕЖДАНЕ НА СТРАНИЦА ────────────────────────────────────────────────────

page = st.session_state.page

if page == "home":
    from pages.page_home import render
    render()
elif page == "profil":
    from pages.page_profil import render
    render()
elif page == "imot":
    from pages.page_imot import render
    render()
elif page == "strategii":
    from pages.page_strategii import render
    render()
elif page == "checklist":
    from pages.page_checklist import render
    render()
elif page == "remont":
    from pages.page_remont import render
    render()
