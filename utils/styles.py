"""
CSS стилове — премиум тъмна тема.
Злато само за 1-2 ключови елемента на страница.
"""
from __future__ import annotations

DARK_THEME_CSS = """
<style>
/* ═══ СКРИЙ STREAMLIT CHROME ═══════════════════════════════════════════ */
[data-testid="stSidebarNav"]  { display: none !important; }
[data-testid="stDeployButton"] { display: none !important; }
#MainMenu                      { display: none !important; }
footer                         { display: none !important; }

/* ═══ ЦВЕТОВА СИСТЕМА ══════════════════════════════════════════════════ */
:root {
    --bg-primary:    #0f1117;
    --bg-secondary:  #141824;
    --bg-card:       #181d2b;
    --bg-card-hover: #1e2438;
    --bg-sidebar:    #111520;

    --gold:          #c9a84c;
    --gold-light:    #ddb96a;
    --gold-dim:      #7a6130;

    --text-primary:  #e8eaf0;
    --text-secondary:#9ca3af;
    --text-muted:    #5a6070;
    --text-section:  #6b7585;

    --green:         #4caf82;
    --red:           #e74c3c;
    --yellow:        #f0c040;
    --blue:          #4a6fa5;

    --border:        #1e2535;
    --border-card:   #232a3a;
    --border-input:  #2a3245;

    --radius-card: 10px;
    --radius-btn:  8px;
}

/* ═══ БАЗОВ ФОН ════════════════════════════════════════════════════════ */
.stApp { background-color: var(--bg-primary); }
.block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 1200px; }

/* ═══ SIDEBAR ══════════════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background-color: var(--bg-sidebar) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1rem 0.75rem !important;
}

/* Всички sidebar бутони — reset до прозрачни */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    color: #8892a0 !important;
    border: none !important;
    border-radius: var(--radius-btn) !important;
    font-weight: 400 !important;
    font-size: 0.9rem !important;
    text-align: left !important;
    padding: 0.5rem 0.75rem !important;
    margin-bottom: 4px !important;
    transition: background 0.15s, color 0.15s !important;
    box-shadow: none !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #1a2030 !important;
    color: var(--text-primary) !important;
    border: none !important;
}
/* Активна страница — primary button в sidebar */
[data-testid="stSidebar"] .stButton > button[kind="primary"],
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"] {
    background: #1e2530 !important;
    color: var(--text-primary) !important;
    border-left: 3px solid var(--gold) !important;
    border-radius: 0 var(--radius-btn) var(--radius-btn) 0 !important;
    font-weight: 600 !important;
    padding-left: 0.9rem !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]:hover,
[data-testid="stSidebar"] .stButton > button[data-testid="baseButton-primary"]:hover {
    background: #232e42 !important;
    opacity: 1 !important;
}

/* ═══ ЗАГЛАВИЯ ════════════════════════════════════════════════════════ */
h1 {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
    margin-bottom: 0.25rem !important;
}
h2 {
    color: #b0b8c4 !important;
    font-weight: 600 !important;
}
h3 {
    color: #b0b8c4 !important;
    font-weight: 500 !important;
}
p { color: var(--text-secondary); }

/* ═══ ГЛОБАЛНИ БУТОНИ ════════════════════════════════════════════════ */
/* Primary (само важни CTA) — злато */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #7a6130 0%, var(--gold) 100%) !important;
    color: #0f1117 !important;
    border: none !important;
    border-radius: var(--radius-btn) !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    transition: opacity 0.2s !important;
    box-shadow: 0 2px 8px rgba(201,168,76,0.15) !important;
}
.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="baseButton-primary"]:hover {
    opacity: 0.88 !important;
}

/* Secondary — outline сив */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"],
.stButton > button:not([kind="primary"]):not([data-testid="baseButton-primary"]) {
    background: transparent !important;
    color: var(--text-secondary) !important;
    border: 1px solid #2e3a50 !important;
    border-radius: var(--radius-btn) !important;
    font-weight: 400 !important;
    transition: border-color 0.15s, color 0.15s !important;
    box-shadow: none !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button[data-testid="baseButton-secondary"]:hover {
    border-color: #4a5570 !important;
    color: var(--text-primary) !important;
    background: #1a2030 !important;
}

/* ═══ INPUTS ══════════════════════════════════════════════════════════ */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > div > textarea {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border: 1px solid var(--border-input) !important;
    border-radius: 6px !important;
    transition: border-color 0.2s !important;
}
.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--gold-dim) !important;
    box-shadow: 0 0 0 1px var(--gold-dim) !important;
    outline: none !important;
}
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--border-input) !important;
}
.stSlider { color: var(--text-secondary) !important; }
[data-testid="stWidgetLabel"] { color: var(--text-secondary) !important; }

/* ═══ КАРТИ ══════════════════════════════════════════════════════════ */
.rm-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-radius: var(--radius-card);
    padding: 1.25rem 1.5rem;
    margin-bottom: 0.875rem;
    transition: border-color 0.2s;
}
.rm-card:hover { border-color: #2e3a50; }

/* Само препоръчаната стратегия / главен CTA */
.rm-card-gold {
    background: linear-gradient(135deg, var(--bg-card) 0%, #18150a 100%);
    border: 1px solid #3a2d10;
    border-radius: var(--radius-card);
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ═══ МЕТРИКИ ════════════════════════════════════════════════════════ */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 8px !important;
    padding: 0.875rem 1rem !important;
}
[data-testid="metric-container"] label {
    color: var(--text-muted) !important;
    font-size: 0.78rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: var(--text-primary) !important;
    font-weight: 700 !important;
}
[data-testid="metric-container"] [data-testid="stMetricDelta"] {
    font-size: 0.8rem !important;
}

/* ═══ ТАБЛИЦИ ════════════════════════════════════════════════════════ */
.stDataFrame, .stDataFrame iframe {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 8px !important;
}

/* ═══ РАЗДЕЛИТЕЛИ ════════════════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1.5rem 0 !important;
}

/* ═══ EXPANDER ═══════════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-card) !important;
    border-radius: 8px !important;
}
[data-testid="stExpander"] summary {
    color: var(--text-secondary) !important;
}

/* ═══ TABS ════════════════════════════════════════════════════════════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.5rem 1.25rem !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text-primary) !important;
    border-bottom: 2px solid var(--gold) !important;
}

/* ═══ ALERTS / MESSAGES ═════════════════════════════════════════════ */
.stSuccess > div {
    background: #0d2018 !important;
    border: 1px solid #1a4a30 !important;
    color: var(--green) !important;
    border-radius: 8px !important;
}
.stError > div {
    background: #200d0d !important;
    border: 1px solid #4a1a1a !important;
    border-radius: 8px !important;
}
.stInfo > div {
    background: #0d1a28 !important;
    border: 1px solid #1a3048 !important;
    border-radius: 8px !important;
}
.stWarning > div {
    background: #201808 !important;
    border: 1px solid #4a3a10 !important;
    border-radius: 8px !important;
}

/* ═══ ПРОГРЕС БАР ════════════════════════════════════════════════════ */
.rm-progress-bar {
    height: 6px;
    background: var(--bg-secondary);
    border-radius: 3px;
    overflow: hidden;
    margin: 0.5rem 0;
}
.rm-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--gold-dim), var(--gold));
    border-radius: 3px;
    transition: width 0.4s ease;
}

/* ═══ BADGE-ОВЕ ══════════════════════════════════════════════════════ */
.rm-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
/* Тъмни приглушени варианти */
.rm-badge-green  { background: #0d2018; color: #4caf82; border: 1px solid #1a3a28; }
.rm-badge-yellow { background: #201808; color: #f0c040; border: 1px solid #3a2e10; }
.rm-badge-red    { background: #200d0d; color: #e74c3c; border: 1px solid #3a1818; }
.rm-badge-gold   { background: #1a1408; color: var(--gold); border: 1px solid var(--gold-dim); }
.rm-badge-blue   { background: #0a1525; color: #6b9fd4; border: 1px solid #1a3050; }
.rm-badge-gray   { background: #1a2030; color: #8892a0; border: 1px solid #2a3045; }

/* ═══ СЕКЦИОННИ ЗАГЛАВИЯ ════════════════════════════════════════════ */
.rm-section-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--text-section);
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    margin: 1.5rem 0 1rem 0;
}

/* ═══ СТРАТЕГИИ ═════════════════════════════════════════════════════ */
.strategia-card {
    background: var(--bg-card);
    border: 1px solid var(--border-card);
    border-left: 3px solid #2e3a50;
    border-radius: var(--radius-card);
    padding: 1.1rem 1.4rem;
    margin-bottom: 0.75rem;
    transition: border-left-color 0.2s;
}
.strategia-card.best {
    border-left-color: var(--gold);
    background: linear-gradient(135deg, var(--bg-card) 0%, #18150a 100%);
}

/* ═══ TRAFFIC LIGHT ══════════════════════════════════════════════════ */
.tl-green  { color: var(--green); font-size: 1.1rem; }
.tl-yellow { color: var(--yellow); font-size: 1.1rem; }
.tl-red    { color: var(--red); font-size: 1.1rem; }

/* ═══ ИНДИКАТОР НА СТРАНИЦА ═════════════════════════════════════════ */
.page-indicator {
    font-size: 0.68rem;
    color: var(--text-muted);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.2rem;
}

/* ═══ ЧЕКЛИСТ ════════════════════════════════════════════════════════ */
.checklist-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
}
.checklist-item:last-child { border-bottom: none; }

/* ═══ ЧИСЛА И СТОЙНОСТИ ════════════════════════════════════════════ */
.rm-value        { color: var(--text-primary); font-weight: 700; }
.rm-value-gold   { color: var(--gold); font-weight: 700; }
.rm-value-green  { color: var(--green); font-weight: 700; }
.rm-value-red    { color: var(--red); font-weight: 700; }
.rm-positive     { color: var(--green); }
.rm-negative     { color: var(--red); }

/* ═══ ЛИНКОВЕ ════════════════════════════════════════════════════════ */
a { color: var(--gold-dim) !important; text-decoration: none !important; }
a:hover { color: var(--gold) !important; text-decoration: underline !important; }

/* ═══ SCROLLBAR ═════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg-primary); }
::-webkit-scrollbar-thumb { background: #2a3245; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #3a4560; }
</style>
"""


# ─────────────────────────────────────────────────────────────
# ПОМОЩНИ ФУНКЦИИ
# ─────────────────────────────────────────────────────────────

def card(content: str, gold: bool = False) -> str:
    cls = "rm-card-gold" if gold else "rm-card"
    return f'<div class="{cls}">{content}</div>'


def section_label(text: str) -> str:
    """Секционно заглавие — CAPS, letter-spacing, тънка линия."""
    return f'<p class="rm-section-label">{text}</p>'


def badge(text: str, variant: str = "gray") -> str:
    return f'<span class="rm-badge rm-badge-{variant}">{text}</span>'


def traffic_light(value: float, good_above: float, bad_below: float,
                  prefix: str = "", suffix: str = "") -> str:
    formatted = f"{prefix}{value:,.0f}{suffix}"
    if value >= good_above:
        return f'<span class="tl-green">▲ {formatted}</span>'
    elif value <= bad_below:
        return f'<span class="tl-red">▼ {formatted}</span>'
    else:
        return f'<span class="tl-yellow">● {formatted}</span>'


def format_eur(amount: float, decimals: int = 0) -> str:
    if decimals == 0:
        return f"€{amount:,.0f}"
    return f"€{amount:,.{decimals}f}"


def format_pct(value: float, decimals: int = 1) -> str:
    return f"{value:.{decimals}f}%"


def risk_color(risk: str) -> str:
    mapping = {
        "Много висок": "red",
        "Висок":       "yellow",
        "Среден":      "yellow",
        "Нисък-Среден": "green",
        "Нисък":       "green",
    }
    return mapping.get(risk, "gold")


# Plotly тема — приглушена палитра
PLOTLY_DARK = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor":  "rgba(0,0,0,0)",
    "font": {"color": "#9ca3af", "family": "system-ui, sans-serif", "size": 12},
}

PLOTLY_COLORS = ["#c9a84c", "#4a6fa5", "#4caf82", "#7c8db0", "#e07040", "#8b5cf6"]
