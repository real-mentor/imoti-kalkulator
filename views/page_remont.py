"""Страница 6 — Ремонт."""
from __future__ import annotations
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import date, timedelta

from utils.styles import format_eur, PLOTLY_DARK
from utils.market_data import REMONT_RAZKHODI, REMONT_REZERV_PCT

FAZI_REMONT = [
    {
        "faza": "Подготовка",
        "color": "#718096",
        "zadata": [
            "Получаване на ключа",
            "Общ преглед и снимки",
            "Измерване на всички стаи",
            "Изготвяне на план за ремонт",
            "Набавяне на оферти (мин. 3)",
        ],
        "den_start": 1,
        "prodylzhitelnost": 3,
    },
    {
        "faza": "Разрушаване / Демонтаж",
        "color": "#e53e3e",
        "zadata": [
            "Премахване на стари облицовки",
            "Демонтаж на санитарни",
            "Демонтаж на подови настилки",
            "Изнасяне на отпадъци",
        ],
        "den_start": 4,
        "prodylzhitelnost": 5,
    },
    {
        "faza": "Груб строеж",
        "color": "#c05621",
        "zadata": [
            "Изграждане/събаряне на стени",
            "Замазка",
            "Шпакловка (сухо строителство)",
            "Мазилка и шпакловка стени",
        ],
        "den_start": 9,
        "prodylzhitelnost": 10,
    },
    {
        "faza": "Електрическа инсталация",
        "color": "#d69e2e",
        "zadata": [
            "Смяна на ел. таблото",
            "Полагане на кабели",
            "Монтаж на контакти и ключове",
            "Тест и приемане",
        ],
        "den_start": 9,
        "prodylzhitelnost": 7,
    },
    {
        "faza": "ВиК инсталация",
        "color": "#2b6cb0",
        "zadata": [
            "Смяна на водопроводни тръби",
            "Канализация",
            "Монтаж санитарни",
            "Тест за течове",
        ],
        "den_start": 10,
        "prodylzhitelnost": 7,
    },
    {
        "faza": "Баня и кухня",
        "color": "#285e61",
        "zadata": [
            "Облицовка с теракот",
            "Монтаж санитарен фаянс",
            "Кухненски шкафове",
            "Мивка и смесители",
        ],
        "den_start": 22,
        "prodylzhitelnost": 10,
    },
    {
        "faza": "Довършителни",
        "color": "#553c9a",
        "zadata": [
            "Монтаж подови настилки",
            "Боядисване",
            "Монтаж врати",
            "Прозорци и первази",
            "Монтаж осветление",
        ],
        "den_start": 32,
        "prodylzhitelnost": 14,
    },
    {
        "faza": "Обзавеждане и финал",
        "color": "#c9a84c",
        "zadata": [
            "Монтаж мебели",
            "Бяла техника",
            "Финално почистване",
            "Фотосесия",
            "Готов за наем/продажба",
        ],
        "den_start": 46,
        "prodylzhitelnost": 10,
    },
]

CHECKLIST_REMONT = {
    "Фаза 0: Преди ремонт": [
        ("r00", "Получил ключове от имота"),
        ("r01", "Направил общ преглед и снимки"),
        ("r02", "Измерил всички стаи (дължина, ширина, височина)"),
        ("r03", "Изготвен план на разпределението"),
        ("r04", "Набавени минимум 3 оферти"),
        ("r05", "Подписан договор с изпълнител"),
        ("r06", "Договорена схема на плащане 30/30/30/10"),
    ],
    "Фаза 1: Разрушаване": [
        ("r10", "Демонтирани стари облицовки"),
        ("r11", "Демонтирани санитарни съоръжения"),
        ("r12", "Демонтирани подови настилки"),
        ("r13", "Изнесени строителни отпадъци"),
    ],
    "Фаза 2: Инсталации": [
        ("r20", "Електрическа инсталация — завършена и тествана"),
        ("r21", "ВиК инсталация — завършена и тествана"),
        ("r22", "Отопление — проверено"),
        ("r23", "Протокол за приемане на инсталациите"),
    ],
    "Фаза 3: Груби работи": [
        ("r30", "Замазка — положена и изсъхнала"),
        ("r31", "Шпакловка — стени и тавани"),
        ("r32", "Зидария — завършена"),
    ],
    "Фаза 4: Баня и кухня": [
        ("r40", "Теракот баня — положен"),
        ("r41", "Санитарен фаянс — монтиран"),
        ("r42", "Кухненски плот и шкафове — монтирани"),
    ],
    "Фаза 5: Довършителни": [
        ("r50", "Подови настилки — положени"),
        ("r51", "Боядисване — завършено"),
        ("r52", "Врати — монтирани"),
        ("r53", "Прозорци — монтирани и зашпакловани"),
        ("r54", "Осветление — монтирано"),
    ],
    "Фаза 6: Финал": [
        ("r60", "Мебели — монтирани"),
        ("r61", "Бяла техника — монтирана и тествана"),
        ("r62", "Финално почистване"),
        ("r63", "Снимки за обява"),
        ("r64", "Готов за наем / продажба"),
    ],
}


def render():
    im = st.session_state.imot

    st.markdown('<p class="page-indicator">ИЗПЪЛНЕНИЕ</p>', unsafe_allow_html=True)
    st.markdown("# 🔨 График за ремонт")
    st.markdown(
        '<p style="color:#9ca3af">Gantt chart за 8 седмици ремонт · Чеклист по фази · ROI на ремонтите</p>',
        unsafe_allow_html=True,
    )

    # ── БЮДЖЕТ ──────────────────────────────────────────────────────────────
    st.markdown("### 💰 Бюджет за ремонт")

    col1, col2, col3 = st.columns(3)
    with col1:
        tip_remont = st.selectbox(
            "Вид ремонт",
            list(REMONT_RAZKHODI.keys()),
            index=3,
        )
        cena_kvm = REMONT_RAZKHODI[tip_remont]
        st.caption(f"Диапазон: €{cena_kvm[0]}–{cena_kvm[1]}/кв.м")

    with col2:
        kvm_remont = st.number_input(
            "Площ за ремонт (кв.м)",
            min_value=10.0, max_value=1000.0, step=5.0,
            value=float(im.get("kvadraturi", 65)),
        )
    with col3:
        start_date = st.date_input("Начална дата на ремонта", value=date.today())

    min_byudjet = cena_kvm[0] * kvm_remont
    sred_byudjet = cena_kvm[2] * kvm_remont
    max_byudjet = cena_kvm[1] * kvm_remont
    rezerv = sred_byudjet * REMONT_REZERV_PCT

    b1, b2, b3, b4 = st.columns(4)
    with b1:
        st.metric("Мин. бюджет", format_eur(min_byudjet))
    with b2:
        st.metric("Среден бюджет", format_eur(sred_byudjet))
    with b3:
        st.metric("Макс. бюджет", format_eur(max_byudjet))
    with b4:
        st.metric(f"+ Резерв ({REMONT_REZERV_PCT*100:.0f}%)", format_eur(rezerv),
                  delta=f"Общо: {format_eur(sred_byudjet + rezerv)}")

    # ── GANTT CHART ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📅 Линеен график (Gantt)")

    gantt_rows = []
    for faza in FAZI_REMONT:
        start = start_date + timedelta(days=faza["den_start"] - 1)
        end = start + timedelta(days=faza["prodylzhitelnost"])
        gantt_rows.append({
            "Фаза": faza["faza"],
            "Начало": start,
            "Край": end,
            "Цвят": faza["color"],
        })

    df_gantt = pd.DataFrame(gantt_rows)

    fig_gantt = px.timeline(
        df_gantt,
        x_start="Начало",
        x_end="Край",
        y="Фаза",
        color="Фаза",
        color_discrete_sequence=[f["color"] for f in FAZI_REMONT],
        title="График за ремонт (~8 седмици)",
    )
    fig_gantt.update_yaxes(autorange="reversed")
    fig_gantt.update_layout(
        **PLOTLY_DARK,
        height=380,
        showlegend=False,
        margin=dict(l=10, r=10, t=40, b=20),
        xaxis=dict(gridcolor="#2d3151"),
        yaxis=dict(gridcolor="#2d3151"),
    )
    st.plotly_chart(fig_gantt, use_container_width=True)

    # ── ROI КАЛКУЛАТОР ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📈 ROI на ремонтите")

    roi_data = [
        {"Вид ремонт": "🖌️ Боядисване (цял имот)", "Разход мин €": 1000, "Разход макс €": 3000, "Добавена ст. мин €": 3000, "Добавена ст. макс €": 8000, "ROI%": "200–400%", "Препоръка": "✅ Задължително"},
        {"Вид ремонт": "🚿 Пълен ремонт баня", "Разход мин €": 4000, "Разход макс €": 10000, "Добавена ст. мин €": 8000, "Добавена ст. макс €": 18000, "ROI%": "150–200%", "Препоръка": "✅ Силен ROI"},
        {"Вид ремонт": "🍳 Кухня — нова", "Разход мин €": 3000, "Разход макс €": 8000, "Добавена ст. мин €": 5000, "Добавена ст. макс €": 15000, "ROI%": "100–150%", "Препоръка": "✅ Добър ROI"},
        {"Вид ремонт": "🚪 Врати и подове", "Разход мин €": 2000, "Разход макс €": 6000, "Добавена ст. мин €": 3000, "Добавена ст. макс €": 10000, "ROI%": "50–100%", "Препоръка": "✅ Препоръчително"},
        {"Вид ремонт": "⚡ Ел. инсталация", "Разход мин €": 2000, "Разход макс €": 5000, "Добавена ст. мин €": 2000, "Добавена ст. макс €": 6000, "ROI%": "20–60%", "Препоръка": "🔴 Задълж. безопасност"},
        {"Вид ремонт": "💧 ВиК инсталация", "Разход мин €": 1500, "Разход макс €": 4000, "Добавена ст. мин €": 1500, "Добавена ст. макс €": 5000, "ROI%": "20–50%", "Препоръка": "🔴 Задълж. безопасност"},
    ]

    st.dataframe(pd.DataFrame(roi_data), use_container_width=True, hide_index=True)

    # ── СХЕМА НА ПЛАЩАНЕ ─────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 💳 Схема на плащане 30/30/30/10")

    byudjet_input = st.number_input(
        "Стойност на договора (€)",
        min_value=0.0, max_value=500000.0, step=500.0,
        value=float(sred_byudjet),
    )

    schema = [
        ("Фаза 1", "ПРЕДИ СТАРТ", 0.30, "Подписан договор, одобрени материали"),
        ("Фаза 2", "АКТ 14 / ГРУБИ", 0.30, "Завършени груби работи, инсталации"),
        ("Фаза 3", "ДОВЪРШИТЕЛНИ", 0.30, "Завършени довършителни работи"),
        ("Фаза 4", "ФИНАЛ", 0.10, "Пълно финално приемане"),
    ]

    sch_cols = st.columns(4)
    for i, (faza, opis, dyal, bel) in enumerate(schema):
        suma = byudjet_input * dyal
        with sch_cols[i]:
            st.markdown(
                f"""
                <div class="rm-card" style="text-align:center">
                    <p style="color:#9ca3af;font-size:0.7rem;margin:0">{faza}</p>
                    <p style="color:#c9a84c;font-size:1.5rem;font-weight:700;margin:0">{int(dyal*100)}%</p>
                    <p style="color:#e8eaf0;font-size:1rem;font-weight:600;margin:0">{format_eur(suma)}</p>
                    <p style="color:#9ca3af;font-size:0.72rem;margin:0.25rem 0 0 0">{opis}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown(
        '<p style="color:#f6e05e;font-size:0.85rem;margin-top:0.5rem">'
        '⚠️ <strong>Правило:</strong> Плащаш следващата фаза САМО след приемане на предишната. '
        'Винаги снимай и документирай преди плащане.</p>',
        unsafe_allow_html=True,
    )

    # ── ЧЕКЛИСТ РЕМОНТ ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### ✅ Чеклист за ремонт")

    if "checklist_remont_state" not in st.session_state:
        st.session_state.checklist_remont_state = {
            k: False
            for items in CHECKLIST_REMONT.values()
            for (k, _) in items
        }

    ck_rem = st.session_state.checklist_remont_state
    total_rem = sum(len(v) for v in CHECKLIST_REMONT.values())
    done_rem = sum(1 for v in ck_rem.values() if v)
    pct_rem = done_rem / total_rem * 100 if total_rem > 0 else 0

    st.markdown(
        f"""
        <div style="margin-bottom:1rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem">
                <span style="color:#9ca3af;font-size:0.85rem">Прогрес: {done_rem}/{total_rem}</span>
                <span style="color:#c9a84c;font-weight:600">{pct_rem:.0f}%</span>
            </div>
            <div class="rm-progress-bar">
                <div class="rm-progress-fill" style="width:{pct_rem}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    for faza_name, items in CHECKLIST_REMONT.items():
        faza_done = sum(1 for (k, _) in items if ck_rem.get(k, False))
        with st.expander(
            f"{'✅' if faza_done == len(items) else '🔄' if faza_done > 0 else '⬜'}  {faza_name}  ·  {faza_done}/{len(items)}",
            expanded=False,
        ):
            for (key, tekst) in items:
                col_chk, col_txt = st.columns([0.06, 0.94])
                with col_chk:
                    ck_rem[key] = st.checkbox("", value=ck_rem.get(key, False), key=f"rem_{key}")
                with col_txt:
                    color = "#e8eaf0" if ck_rem.get(key) else "#9ca3af"
                    strike = "text-decoration:line-through;opacity:0.6;" if ck_rem.get(key) else ""
                    st.markdown(
                        f'<p style="color:{color};{strike}margin:0;padding:0.15rem 0;font-size:0.9rem">{tekst}</p>',
                        unsafe_allow_html=True,
                    )

    st.session_state.checklist_remont_state = ck_rem
