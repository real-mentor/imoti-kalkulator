"""
Real Mentor — Калкулатор за имотни инвестиции в България
Главен файл: auth, навигация и session state.
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

# ─── SESSION STATE ────────────────────────────────────────────

def init_state():
    defaults = {
        "page": "home",
        "user": None,          # {"id": ..., "email": ...} при логнат
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
        "imot": {
            "vid_imot": "2-стаен",
            "cena": 150000.0,
            "kvadraturi": 65.0,
            "grad": "София",
            "zona": "Лозенец",
            "etaj": 3,
            "obshto_etaji": 8,
            "izlozhenie": "Юг",
            "tip_stroitelstvo": "Ново строителство",  # Ново строителство | Монолит (2000–2010) | Старо — тухла / ЕПК | Старо — панел
            "etap": "Акт 16 (готов нов)",
            "ochakvаn_naem": 0.0,
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

# ─── AUTH GATE ────────────────────────────────────────────────
# Ако не е логнат → показва Login/Register страница

if st.session_state.user is None:
    from views.page_auth import render as render_auth
    render_auth()
    st.stop()

# ─── НАВИГАЦИЯ (само за логнати) ──────────────────────────────

PAGES = {
    "home":       ("🏠", "Начало"),
    "profil":     ("👤", "Профил"),
    "imot":       ("🏗️", "Оценка на имот"),
    "strategii":  ("📊", "Стратегии"),
    "moite_imoti":("📋", "Моите имоти"),
    "checklist":  ("✅", "Чеклист"),
    "remont":     ("🔨", "Ремонт"),
    "settings":   ("⚙️", "Настройки"),
}

with st.sidebar:
    st.markdown(
        '<p style="color:#c9a84c;font-weight:700;font-size:1.1rem;margin-bottom:0">Real Mentor</p>'
        '<p style="color:#6b7280;font-size:0.75rem;margin-top:0;margin-bottom:1rem">Имотен Калкулатор</p>',
        unsafe_allow_html=True,
    )

    # Имейл на потребителя
    email = st.session_state.user.get("email", "")
    st.markdown(
        f'<div style="background:#1e2235;border:1px solid #2d3151;border-radius:8px;'
        f'padding:0.5rem 0.75rem;margin-bottom:1rem">'
        f'<p style="color:#9ca3af;font-size:0.65rem;margin:0">ЛОГНАТ КАТО</p>'
        f'<p style="color:#c9a84c;font-size:0.8rem;margin:0;word-break:break-all">{email}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    for page_id, (icon, label) in PAGES.items():
        is_active = st.session_state.page == page_id
        btn_type = "primary" if is_active else "secondary"
        if st.button(f"{icon}  {label}", key=f"nav_{page_id}", use_container_width=True, type=btn_type):
            st.session_state.page = page_id
            st.rerun()

    st.markdown("---")

    if st.button("🚪  Излез", use_container_width=True):
        from utils.database import logout
        logout()
        st.session_state.user = None
        st.session_state.page = "home"
        st.rerun()

    st.markdown(
        '<p style="color:#6b7280;font-size:0.7rem;text-align:center;margin-top:0.5rem">'
        'Real Mentor · 2026<br>Данни: Q1 2026</p>',
        unsafe_allow_html=True,
    )

# ─── ЗАРЕЖДАНЕ НА СТРАНИЦА ────────────────────────────────────

page = st.session_state.page

if page == "home":
    from views.page_home import render
    render()
elif page == "profil":
    from views.page_profil import render
    render()
elif page == "imot":
    from views.page_imot import render
    render()
elif page == "strategii":
    from views.page_strategii import render
    render()
elif page == "moite_imoti":
    from views.page_moite_imoti import render
    render()
elif page == "checklist":
    from views.page_checklist import render
    render()
elif page == "remont":
    from views.page_remont import render
    render()
elif page == "settings":
    from views.page_settings import render
    render()
