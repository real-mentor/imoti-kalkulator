"""Страница 4 — Сравнение на 7 стратегии."""
from __future__ import annotations
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional

from utils.market_data import (
    PROGRES_KOEFICIENTI, RISK_ETAP, INFLACIYA_GOD, PAZARNO_POSKAPVANE_GOD,
)
from utils.calculations import (
    mesechna_vnоska, noi, cap_rate, cash_on_cash,
    mesecen_pаricen_potok, payback_period, fix_flip_analiz, buy_hold_analiz,
)
from utils.price_model import kapital_pechalba, badeshta_cena, meseci_do_akt16
from utils.recommendation import preporycha_strategia, risk_badge
from utils.styles import format_eur, format_pct, badge

PLOTLY_DARK = {
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#e8eaf0", "family": "sans-serif"},
}


def _risk_emoji(risk: str) -> str:
    m = {"Много висок": "🔴", "Висок": "🟠", "Среден": "🟡", "Нисък-Среден": "🟢", "Нисък": "🟢"}
    return m.get(risk, "⚪")


def render():
    im = st.session_state.imot
    profil = st.session_state.profil

    pokupna = im["cena"]
    kvm = im["kvadraturi"]
    etap = im["etap"]
    naem = im["ochakvаn_naem"]
    remont = im["remont_byudzhet"]
    samoych_pct = im["samoychastie_pct"]
    lihva = im["lihva"]
    srok_god = im["srok_god"]
    notarialni_pct = im["notarialni_pct"]

    samoych_eur = pokupna * samoych_pct
    kredit_eur = pokupna * (1 - samoych_pct)
    notarialni_eur = pokupna * notarialni_pct
    vnоska = mesechna_vnоska(kredit_eur, lihva, srok_god)
    meseci_stroit = meseci_do_akt16(etap)
    godini_stroit = meseci_stroit / 12

    st.markdown('<p class="page-indicator">ЯДРОТО</p>', unsafe_allow_html=True)
    st.markdown("# 📊 Сравнение на 7 стратегии")
    st.markdown(
        f'<p style="color:#9ca3af">Имот: <strong style="color:#c9a84c">{format_eur(pokupna)}</strong> · '
        f'{kvm:.0f} кв.м · {im["grad"]} / {im["zona"]} · {etap}</p>',
        unsafe_allow_html=True,
    )

    # ═══════════════════════════════════════════════════
    # ИЗЧИСЛЕНИЯ ЗА ВСЯКА СТРАТЕГИЯ
    # ═══════════════════════════════════════════════════

    # — С1: На зелено (и преди разрешение) —
    def strat_zeleno(etap_name: str) -> dict:
        rez = kapital_pechalba(
            pokupna, etap_name, godini_stroit,
            notarialni_pct=notarialni_pct, prodajbeni_razkhodi_pct=0.025,
        )
        nachaln = samoych_eur + notarialni_eur
        return {
            "ime": f"{'🏗️ Покупка на зелено' if 'зелено' in etap_name else '📋 Преди разрешение'}",
            "etap": etap_name,
            "vlozhenie": nachaln,
            "pechalba": rez["brutna_pechalba"],
            "roi_pct": rez["roi_pct"],
            "srok_mes": meseci_do_akt16(etap_name),
            "risk": RISK_ETAP.get(etap_name, "Среден"),
            "detayli": rez,
        }

    s1 = strat_zeleno("На зелено (след разрешение)")
    s2 = strat_zeleno("Преди разрешение за строеж")

    # — С3: Акт 14/15 —
    def strat_akt(etap_name: str) -> dict:
        rez = kapital_pechalba(pokupna, etap_name, meseci_do_akt16(etap_name) / 12, notarialni_pct=notarialni_pct)
        nachaln = samoych_eur + notarialni_eur
        return {
            "ime": f"🧱 {etap_name}",
            "etap": etap_name,
            "vlozhenie": nachaln,
            "pechalba": rez["brutna_pechalba"],
            "roi_pct": rez["roi_pct"],
            "srok_mes": meseci_do_akt16(etap_name),
            "risk": RISK_ETAP.get(etap_name, "Среден"),
            "detayli": rez,
        }

    s3 = strat_akt("Акт 14 (груб строеж)")

    # — С4: Наем —
    noi_val = noi(naem, pokupna)
    cr = cap_rate(noi_val, pokupna)
    coc = cash_on_cash(naem, pokupna, vnоska, samoych_eur + notarialni_eur + remont)
    mes_cf = mesecen_pаricen_potok(naem, pokupna, vnоska)
    pb = payback_period(samoych_eur, notarialni_eur, remont, mes_cf)

    s4 = {
        "ime": "🏠 Покупка с цел наем",
        "etap": etap,
        "vlozhenie": samoych_eur + notarialni_eur + remont,
        "pechalba": (noi_val * 10) if noi_val > 0 else 0,  # 10 год. NOI
        "roi_pct": coc,
        "srok_mes": 12,
        "risk": "Нисък",
        "detayli": {
            "noi": noi_val,
            "cap_rate": cr,
            "cash_on_cash": coc,
            "mes_cf": mes_cf,
            "payback": pb,
            "vnоska": vnоska,
        },
    }

    # — С5: Fix & Flip —
    arv_est = pokupna * 1.25 + remont * 0.7  # ARV оценка
    ff = fix_flip_analiz(pokupna, remont if remont > 0 else pokupna * 0.10, arv_est, notarialni_pct)
    s5 = {
        "ime": "🔨 Fix & Flip",
        "etap": etap,
        "vlozhenie": ff["obshto_vlozhenie"],
        "pechalba": ff["brutna_pechalba"],
        "roi_pct": ff["roi_pct"],
        "srok_mes": ff["obshto_srok_mes"],
        "risk": "Среден-Висок",
        "detayli": ff,
    }

    # — С6: Buy & Hold 7 год. —
    bh = buy_hold_analiz(pokupna, etap, naem, samoych_pct, lihva, srok_god, notarialni_pct, remont, max_godini=10)
    bh7 = bh["po_godini"][7]
    s6 = {
        "ime": "📈 Buy & Hold (7 год.)",
        "etap": etap,
        "vlozhenie": bh["nachaln_vlozhenie"],
        "pechalba": bh7["kapitalov_rezultat"],
        "roi_pct": bh7["roi_pct"],
        "srok_mes": 84,
        "risk": "Нисък",
        "detayli": bh,
    }

    # — С7: Ново готов имот —
    noi_novo = noi(naem, pokupna)
    coc_novo = cash_on_cash(naem, pokupna, vnоska, samoych_eur + notarialni_eur)
    bh_novo = buy_hold_analiz(pokupna, "Акт 16 (готов нов)", naem, samoych_pct, lihva, srok_god, notarialni_pct, 0.0, 10)
    bh_novo_5 = bh_novo["po_godini"][5]
    s7 = {
        "ime": "🏢 Ново стр-во — готов",
        "etap": "Акт 16 (готов нов)",
        "vlozhenie": samoych_eur + notarialni_eur,
        "pechalba": bh_novo_5["kapitalov_rezultat"],
        "roi_pct": coc_novo,
        "srok_mes": 60,
        "risk": "Нисък",
        "detayli": {"noi": noi_novo, "cash_on_cash": coc_novo, "bh": bh_novo},
    }

    strategii = [s1, s2, s3, s4, s5, s6, s7]

    # ═══════════════════════════════════════════════════
    # ДЕТАЙЛИ — 7 СТРАТЕГИИ
    # ═══════════════════════════════════════════════════

    for i, s in enumerate(strategii):
        risk_e = _risk_emoji(s["risk"])
        with st.expander(f"{s['ime']}  ·  ROI {s['roi_pct']:.1f}%  ·  Риск: {risk_e} {s['risk']}", expanded=(i == 3)):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Вложение", format_eur(s["vlozhenie"]))
            with c2:
                st.metric("Очаквана печалба", format_eur(s["pechalba"]))
            with c3:
                st.metric("ROI", format_pct(s["roi_pct"]))
            with c4:
                mes = s["srok_mes"]
                st.metric("Срок", f"{mes} мес. ({mes//12} год. {mes%12} мес.)" if mes > 0 else "Веднага")

            det = s["detayli"]

            # Специфични детайли по стратегия
            if i in [0, 1]:  # Зелено / Преди разрешение
                st.markdown(
                    f"""
                    | Параметър | Стойност |
                    |-----------|---------|
                    | Покупна цена | {format_eur(det['pokupna_cena'])} |
                    | Очаквана Акт 16 цена | {format_eur(det['badeshta_cena'])} |
                    | Строителен прогрес | ×{PROGRES_KOEFICIENTI.get(s['etap'], 1):.2f} |
                    | Разходи покупка | {format_eur(det['razkhodi_pokupka'])} |
                    | Разходи продажба | {format_eur(det['razkhodi_prodajba'])} |
                    | Брутна печалба | {format_eur(det['brutna_pechalba'])} |
                    | Годишен ROI | {det['godishen_roi']:.1f}% |
                    """
                )
                st.warning(f"⚠️ **Риск {s['risk']}** — Строителят може да забави или фалира. Проверявай репутацията му!")

            elif i == 2:  # Акт 14/15
                st.markdown(
                    f"""
                    | Параметър | Стойност |
                    |-----------|---------|
                    | Оставащ срок до Акт 16 | {s['srok_mes']} месеца |
                    | Строителен прогрес | ×{PROGRES_KOEFICIENTI.get(s['etap'], 1):.2f} |
                    | Очаквана Акт 16 цена | {format_eur(det['badeshta_cena'])} |
                    | Брутна печалба | {format_eur(det['brutna_pechalba'])} |
                    | ROI | {det['roi_pct']:.1f}% |
                    """
                )

            elif i == 3:  # Наем
                mes_cf = det["mes_cf"]
                cf_color = "#48bb78" if mes_cf >= 0 else "#fc8181"
                pb = det["payback"]
                st.markdown(
                    f"""
                    | Показател | Стойност |
                    |-----------|---------|
                    | Месечен наем | {format_eur(naem)} |
                    | Месечна ипотека | {format_eur(det['vnоska'])} |
                    | NOI (годишен) | {format_eur(det['noi'])} |
                    | Cap Rate | {det['cap_rate']:.2f}% |
                    | Cash-on-Cash Return | {det['cash_on_cash']:.2f}% |
                    | Месечен паричен поток | {format_eur(det['mes_cf'])} |
                    | Срок за пълна възвр. | {f"{pb:.0f} мес. ({pb/12:.1f} год.)" if pb else "Отрицателен CF"} |
                    """
                )

            elif i == 4:  # Fix & Flip
                st.markdown(
                    f"""
                    | Параметър | Стойност |
                    |-----------|---------|
                    | Покупна цена | {format_eur(det['pokupna'])} |
                    | Ремонт | {format_eur(det['remont'])} |
                    | Общо вложение | {format_eur(det['obshto_vlozhenie'])} |
                    | ARV (пазарна след ремонт) | {format_eur(det['arv'])} |
                    | Брутна печалба | {format_eur(det['brutna_pechalba'])} |
                    | ROI | {det['roi_pct']:.1f}% |
                    | Правило 70% | Max покупна: {format_eur(det['max_pokupna_70'])} · {'✅ ОК' if det['pravilo_70_ok'] else '❌ Над лимита'} |
                    | Срок | {det['obshto_srok_mes']} месеца |
                    | Оценка | {det['otsenka_emoji']} {det['otsenka']} |
                    """
                )

            elif i == 5:  # Buy & Hold
                st.markdown("**Прогноза по години:**")
                rows = []
                for g_data in det["po_godini"][1:]:
                    rows.append({
                        "Година": g_data["godina"],
                        "Стойност имот": format_eur(g_data["stojnost_imot"]),
                        "Натрупан наем": format_eur(g_data["natrupen_naem"]),
                        "Остатък кредит": format_eur(g_data["ostatok_kredit"]),
                        "Капиталов резултат": format_eur(g_data["kapitalov_rezultat"]),
                        "ROI %": format_pct(g_data["roi_pct"]),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                # Line chart
                години = [d["godina"] for d in det["po_godini"]]
                stojnosti = [d["stojnost_imot"] for d in det["po_godini"]]
                naemi_cum = [d["natrupen_naem"] for d in det["po_godini"]]
                rez_list = [d["kapitalov_rezultat"] for d in det["po_godini"]]

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=години, y=stojnosti, name="Стойност имот", line=dict(color="#c9a84c", width=2)))
                fig.add_trace(go.Scatter(x=години, y=naemi_cum, name="Натрупан наем", line=dict(color="#63b3ed", width=2)))
                fig.add_trace(go.Scatter(x=години, y=rez_list, name="Капиталов резултат", line=dict(color="#48bb78", width=2, dash="dash")))
                fig.update_layout(
                    **PLOTLY_DARK,
                    height=300,
                    xaxis=dict(title="Година", gridcolor="#2d3151"),
                    yaxis=dict(title="€", gridcolor="#2d3151"),
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    margin=dict(l=0, r=0, t=20, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)

    # ═══════════════════════════════════════════════════
    # СРАВНИТЕЛНА ТАБЛИЦА
    # ═══════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 📋 Сравнителна таблица")

    max_roi = max(s["roi_pct"] for s in strategii)
    min_risk_order = ["Нисък", "Нисък-Среден", "Среден", "Среден-Висок", "Висок", "Много висок"]
    najbezopasnа = min(strategii, key=lambda s: min_risk_order.index(s["risk"]) if s["risk"] in min_risk_order else 99)
    najbyrza = min(strategii, key=lambda s: s["srok_mes"])
    najdobra_roi = max(strategii, key=lambda s: s["roi_pct"])

    tbl_rows = []
    for s in strategii:
        marks = []
        if s["roi_pct"] == max_roi:
            marks.append("🏆 Макс ROI")
        if s is najbezopasnа:
            marks.append("🛡️ Нисък риск")
        if s is najbyrza:
            marks.append("⚡ Най-бърза")
        tbl_rows.append({
            "Стратегия": s["ime"],
            "Вложение €": f"{s['vlozhenie']:,.0f}",
            "Очакв. печалба €": f"{s['pechalba']:,.0f}",
            "ROI %": f"{s['roi_pct']:.1f}%",
            "Срок (мес)": s["srok_mes"],
            "Риск": f"{_risk_emoji(s['risk'])} {s['risk']}",
            "Маркери": "  ".join(marks) if marks else "—",
        })

    st.dataframe(pd.DataFrame(tbl_rows), use_container_width=True, hide_index=True)

    # ═══════════════════════════════════════════════════
    # ГРАФИКИ
    # ═══════════════════════════════════════════════════
    st.markdown("### 📈 Визуализации")

    col1, col2 = st.columns(2)

    with col1:
        # Bar chart ROI
        colors = ["#c9a84c" if s["roi_pct"] == max_roi else "#2d3151" for s in strategii]
        fig_roi = go.Figure(go.Bar(
            x=[s["ime"].split(" ", 1)[1] if " " in s["ime"] else s["ime"] for s in strategii],
            y=[s["roi_pct"] for s in strategii],
            marker_color=colors,
            text=[f"{s['roi_pct']:.1f}%" for s in strategii],
            textposition="outside",
        ))
        fig_roi.update_layout(
            **PLOTLY_DARK,
            title="ROI % по стратегии",
            height=350,
            xaxis=dict(tickangle=-30, gridcolor="#2d3151"),
            yaxis=dict(title="%", gridcolor="#2d3151"),
            margin=dict(l=0, r=0, t=40, b=80),
        )
        st.plotly_chart(fig_roi, use_container_width=True)

    with col2:
        # Pie chart структура на инвестицията
        labels = ["Самоучастие", "Кредит", "Нотариални такси"]
        values = [samoych_eur, kredit_eur, notarialni_eur]
        if remont > 0:
            labels.append("Ремонт")
            values.append(remont)
        fig_pie = go.Figure(go.Pie(
            labels=labels,
            values=values,
            hole=0.4,
            marker_colors=["#c9a84c", "#63b3ed", "#fc8181", "#48bb78"],
        ))
        fig_pie.update_layout(
            **PLOTLY_DARK,
            title="Структура на инвестицията",
            height=350,
            margin=dict(l=0, r=0, t=40, b=0),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    # ═══════════════════════════════════════════════════
    # ПРЕПОРЪЧАНА СТРАТЕГИЯ
    # ═══════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 🏆 Препоръчана стратегия ЗА ТЕБ")

    preporyaka = preporycha_strategia(
        risk_tolerans=profil["risk"],
        investicionen_horiont=profil["horiont"],
        svoboden_cash=profil["spestyavane_cash"],
        mesecen_cash_flow_nujda=profil["target_cash_flow"],
        etap=etap,
        max_imot=pokupna * 1.5,
    )

    naj_id = preporyaka["najdobra_strategia"]["id"] if preporyaka["najdobra_strategia"] else "buy_hold"

    # Намери съответстващата стратегия
    id_map = {
        "zeleno": s1, "preди": s2, "akt": s3,
        "naem": s4, "fix_flip": s5, "buy_hold": s6, "novo_gotov": s7,
    }
    препоръчана_стр = id_map.get(naj_id, s6)

    st.markdown(
        f"""
        <div class="rm-card-gold" style="padding:1.5rem">
            <p style="color:#c9a84c;font-size:0.75rem;font-weight:700;margin:0 0 0.5rem 0">
                На база: риск={profil['risk']} · хоризонт={profil['horiont']}
            </p>
            <h2 style="margin:0 0 0.75rem 0;color:#e8eaf0">{препоръчана_стр['ime']}</h2>
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem">
                <div>
                    <p style="color:#9ca3af;font-size:0.75rem;margin:0">ВЛОЖЕНИЕ</p>
                    <p style="color:#c9a84c;font-size:1.2rem;font-weight:700;margin:0">{format_eur(препоръчана_стр['vlozhenie'])}</p>
                </div>
                <div>
                    <p style="color:#9ca3af;font-size:0.75rem;margin:0">ОЧАКВАНА ПЕЧАЛБА</p>
                    <p style="color:#48bb78;font-size:1.2rem;font-weight:700;margin:0">{format_eur(препоръчана_стр['pechalba'])}</p>
                </div>
                <div>
                    <p style="color:#9ca3af;font-size:0.75rem;margin:0">ROI</p>
                    <p style="color:#63b3ed;font-size:1.2rem;font-weight:700;margin:0">{format_pct(препоръчана_стр['roi_pct'])}</p>
                </div>
                <div>
                    <p style="color:#9ca3af;font-size:0.75rem;margin:0">СРОК</p>
                    <p style="color:#e8eaf0;font-size:1.2rem;font-weight:700;margin:0">{препоръчана_стр['srok_mes']} мес.</p>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if preporyaka["najdobra_strategia"]:
        st.markdown(f"💡 {preporyaka['najdobra_strategia']['pricina']}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("✅  Продължи към Чеклист за покупка", type="primary", use_container_width=True):
            st.session_state.page = "checklist"
            st.rerun()
