"""
CSS стилове — премиум тъмна тема с приглушено злато.
"""

DARK_THEME_CSS = """
<style>
/* ─── ОСНОВНИ ЦВЕТОВЕ ─── */
:root {
    --bg-primary:    #0f1117;
    --bg-secondary:  #1a1d2e;
    --bg-card:       #1e2235;
    --bg-card-hover: #252840;
    --gold:          #c9a84c;
    --gold-light:    #e2c27d;
    --gold-dim:      #8a6f35;
    --text-primary:  #e8eaf0;
    --text-secondary:#9ca3af;
    --text-muted:    #6b7280;
    --green:         #48bb78;
    --red:           #fc8181;
    --yellow:        #f6e05e;
    --blue:          #63b3ed;
    --border:        #2d3151;
}

/* ─── ФОН ─── */
.stApp { background-color: var(--bg-primary); }
.block-container { padding: 1.5rem 2rem 3rem 2rem; }

/* ─── СТРАНИЧНА ЛЕНТА ─── */
.css-1d391kg, [data-testid="stSidebar"] {
    background-color: var(--bg-secondary) !important;
    border-right: 1px solid var(--border);
}

/* ─── КАРТИ ─── */
.rm-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.rm-card:hover { border-color: var(--gold-dim); }

.rm-card-gold {
    background: linear-gradient(135deg, var(--bg-card) 0%, #1e1a0e 100%);
    border: 1px solid var(--gold-dim);
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

/* ─── ЗАГЛАВИЯ ─── */
h1 {
    color: var(--gold-light) !important;
    font-weight: 700 !important;
    letter-spacing: -0.02em !important;
}
h2 { color: var(--text-primary) !important; font-weight: 600 !important; }
h3 { color: var(--text-primary) !important; font-weight: 500 !important; }

/* ─── БУТОНИ ─── */
.stButton > button {
    background: linear-gradient(135deg, var(--gold-dim) 0%, var(--gold) 100%);
    color: #0f1117;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    padding: 0.5rem 1.5rem;
    transition: opacity 0.2s;
}
.stButton > button:hover { opacity: 0.85; }

/* ─── INPUTS ─── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div,
.stSlider {
    background-color: var(--bg-secondary) !important;
    color: var(--text-primary) !important;
    border-color: var(--border) !important;
}

/* ─── МЕТРИКИ ─── */
[data-testid="metric-container"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem;
}
[data-testid="metric-container"] label {
    color: var(--text-secondary) !important;
}

/* ─── ТАБЛИЦИ ─── */
.stDataFrame {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 8px;
}

/* ─── РАЗДЕЛИТЕЛИ ─── */
hr { border-color: var(--border) !important; }

/* ─── ПРОГРЕС БАР ─── */
.rm-progress-bar {
    height: 8px;
    background: var(--bg-secondary);
    border-radius: 4px;
    overflow: hidden;
    margin: 0.5rem 0;
}
.rm-progress-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--gold-dim), var(--gold));
    border-radius: 4px;
    transition: width 0.3s;
}

/* ─── BADGE-ОВЕ ─── */
.rm-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.03em;
}
.rm-badge-green  { background: #1c3a28; color: #48bb78; border: 1px solid #2d5a3d; }
.rm-badge-yellow { background: #2d2a10; color: #f6e05e; border: 1px solid #4a4015; }
.rm-badge-red    { background: #3a1c1c; color: #fc8181; border: 1px solid #5a2d2d; }
.rm-badge-gold   { background: #2a1f08; color: #c9a84c; border: 1px solid #3a2d10; }
.rm-badge-blue   { background: #0d2138; color: #63b3ed; border: 1px solid #1a3a5c; }

/* ─── СТРАТЕГИИ КАРТИ ─── */
.strategia-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold-dim);
    border-radius: 10px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
}
.strategia-card.best {
    border-left-color: var(--gold);
    background: linear-gradient(135deg, var(--bg-card) 0%, #201b0a 100%);
}

/* ─── TRAFFIC LIGHT ─── */
.tl-green  { color: #48bb78; font-size: 1.2rem; }
.tl-yellow { color: #f6e05e; font-size: 1.2rem; }
.tl-red    { color: #fc8181; font-size: 1.2rem; }

/* ─── ИНДИКАТОР НА СТРАНИЦА ─── */
.page-indicator {
    font-size: 0.75rem;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-bottom: 0.25rem;
}

/* ─── ЧЕКЛИСТ ─── */
.checklist-item {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--border);
}
.checklist-item:last-child { border-bottom: none; }

/* ─── SIDEBAR НАВИГАЦИЯ ─── */
.sidebar-nav-item {
    padding: 0.6rem 0.8rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    transition: background 0.15s;
}
.sidebar-nav-item:hover { background: var(--bg-card); }
.sidebar-nav-item.active { background: var(--bg-card); border-left: 3px solid var(--gold); }
</style>
"""


def card(content: str, gold: bool = False) -> str:
    """Обвива съдържание в HTML карта."""
    cls = "rm-card-gold" if gold else "rm-card"
    return f'<div class="{cls}">{content}</div>'


def badge(text: str, variant: str = "gold") -> str:
    """HTML badge."""
    return f'<span class="rm-badge rm-badge-{variant}">{text}</span>'


def traffic_light(value: float, good_above: float, bad_below: float, prefix: str = "", suffix: str = "") -> str:
    """Връща цветен индикатор (зелен/жълт/червен)."""
    formatted = f"{prefix}{value:,.0f}{suffix}"
    if value >= good_above:
        return f'<span class="tl-green">▲ {formatted}</span>'
    elif value <= bad_below:
        return f'<span class="tl-red">▼ {formatted}</span>'
    else:
        return f'<span class="tl-yellow">● {formatted}</span>'


def format_eur(amount: float, decimals: int = 0) -> str:
    """Форматира сума в евро."""
    if decimals == 0:
        return f"€{amount:,.0f}"
    return f"€{amount:,.{decimals}f}"


def format_pct(value: float, decimals: int = 1) -> str:
    """Форматира процент."""
    return f"{value:.{decimals}f}%"


def risk_color(risk: str) -> str:
    """Цвят по ниво на риск."""
    mapping = {
        "Много висок": "red",
        "Висок": "yellow",
        "Среден": "yellow",
        "Нисък-Среден": "green",
        "Нисък": "green",
    }
    return mapping.get(risk, "gold")
