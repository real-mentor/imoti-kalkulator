"""Страница 4 — Сравнение на 7 стратегии."""
from __future__ import annotations
from datetime import date
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Optional

from utils.database import save_calculation
from utils.market_data import (
    PROGRES_KOEFICIENTI, RISK_ETAP, INFLACIYA_GOD, PAZARNO_POSKAPVANE_GOD,
    BUY_HOLD_OPERATIVNI_PCT, DANUK_NAEM_PCT,
)
from utils.calculations import (
    mesechna_vnоska, noi, cap_rate, cash_on_cash,
    mesecen_pаricen_potok, payback_period, fix_flip_analiz, buy_hold_analiz,
)
from utils.price_model import kapital_pechalba, badeshta_cena, meseci_do_akt16
from utils.recommendation import preporycha_strategia, risk_badge
from utils.styles import format_eur, format_pct, badge, PLOTLY_DARK


def _risk_emoji(risk: str) -> str:
    m = {"Много висок": "🔴", "Висок": "🟠", "Среден": "🟡", "Нисък-Среден": "🟢", "Нисък": "🟢"}
    return m.get(risk, "⚪")


def _annualized_roi(pechalba: float, vlozhenie: float, srok_mes: float) -> float:
    """Годишна CAGR на вложения собствен капитал."""
    if vlozhenie <= 0 or srok_mes <= 0:
        return 0.0
    years = srok_mes / 12
    return ((1 + pechalba / vlozhenie) ** (1 / years) - 1) * 100


def render():
    im = st.session_state.imot
    profil = st.session_state.profil

    pokupna = im["cena"]
    kvm = im["kvadraturi"]
    etap = im["etap"]
    naem = im["ochakvаn_naem"]

    if naem <= 0:
        st.markdown("# 📊 Сравнение на 7 стратегии")
        st.warning(
            "⚠️ **Въведи очакван месечен наем за по-точна калкулация.**  \n"
            "Отиди в **Оценка на имот** и попълни полето 'Очакван месечен наем (€)' "
            "на база собствено проучване на пазара."
        )
        if st.button("← Обратно към Оценка на имот"):
            st.session_state.page = "imot"
            st.rerun()
        return

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
        srok = meseci_do_akt16(etap_name)
        return {
            "ime": f"{'🏗️ Покупка на зелено' if 'зелено' in etap_name else '📋 Преди разрешение'}",
            "etap": etap_name,
            "vlozhenie": nachaln,
            "pechalba": rez["brutna_pechalba"],
            "pechalba_naem": 0.0,
            "pechalba_poskapvane": rez["brutna_pechalba"],
            "roi_pct": _annualized_roi(rez["brutna_pechalba"], nachaln, srok),
            "srok_mes": srok,
            "risk": RISK_ETAP.get(etap_name, "Среден"),
            "detayli": rez,
        }

    s1 = strat_zeleno("На зелено (след разрешение)")
    s2 = strat_zeleno("Преди разрешение за строеж")

    # — С3: Акт 14/15 —
    def strat_akt(etap_name: str) -> dict:
        srok = meseci_do_akt16(etap_name)
        rez = kapital_pechalba(pokupna, etap_name, srok / 12, notarialni_pct=notarialni_pct)
        nachaln = samoych_eur + notarialni_eur
        return {
            "ime": f"🧱 {etap_name}",
            "etap": etap_name,
            "vlozhenie": nachaln,
            "pechalba": rez["brutna_pechalba"],
            "pechalba_naem": 0.0,
            "pechalba_poskapvane": rez["brutna_pechalba"],
            "roi_pct": _annualized_roi(rez["brutna_pechalba"], nachaln, srok),
            "srok_mes": srok,
            "risk": RISK_ETAP.get(etap_name, "Среден"),
            "detayli": rez,
        }

    s3 = strat_akt("Акт 14 (груб строеж)")

    # — Buy & Hold база (преизползвана от С4 и С6) —
    bh = buy_hold_analiz(pokupna, etap, naem, samoych_pct, lihva, srok_god, notarialni_pct, remont, max_godini=10)

    # — С4: Наем —
    noi_val = noi(naem, pokupna)
    cr = cap_rate(noi_val, pokupna)
    coc = cash_on_cash(naem, pokupna, vnоska, samoych_eur + notarialni_eur + remont)
    mes_cf = mesecen_pаricen_potok(naem, pokupna, vnоska)
    pb = payback_period(samoych_eur, notarialni_eur, remont, mes_cf)
    bh10 = bh["po_godini"][10]

    s4 = {
        "ime": "🏠 Покупка с цел наем",
        "etap": etap,
        "vlozhenie": samoych_eur + notarialni_eur + remont,
        "pechalba": bh10["kapitalov_rezultat"],
        "pechalba_naem": bh10["natrupen_naem"],
        "pechalba_poskapvane": bh10["kapitalov_rezultat"] - bh10["natrupen_naem"],
        "roi_pct": bh10["godishen_roi"],
        "srok_mes": 120,
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
        "pechalba_naem": 0.0,
        "pechalba_poskapvane": ff["brutna_pechalba"],
        "roi_pct": _annualized_roi(ff["brutna_pechalba"], ff["obshto_vlozhenie"], ff["obshto_srok_mes"]),
        "srok_mes": ff["obshto_srok_mes"],
        "risk": "Среден-Висок",
        "detayli": ff,
    }

    # — С6: Buy & Hold 7 год. —
    bh7 = bh["po_godini"][7]
    s6 = {
        "ime": "📈 Buy & Hold (7 год.)",
        "etap": etap,
        "vlozhenie": bh["nachaln_vlozhenie"],
        "pechalba": bh7["kapitalov_rezultat"],
        "pechalba_naem": bh7["natrupen_naem"],
        "pechalba_poskapvane": bh7["kapitalov_rezultat"] - bh7["natrupen_naem"],
        "roi_pct": bh7["godishen_roi"],
        "srok_mes": 84,
        "risk": "Нисък",
        "detayli": bh,
    }

    # — С7: Ново готов имот —
    noi_novo = noi(naem, pokupna)
    coc_novo = cash_on_cash(naem, pokupna, vnоska, samoych_eur + notarialni_eur)
    bh_novo = buy_hold_analiz(pokupna, etap, naem, samoych_pct, lihva, srok_god, notarialni_pct, 0.0, 10)
    bh_novo_5 = bh_novo["po_godini"][5]
    s7 = {
        "ime": "🏢 Ново стр-во — готов",
        "etap": etap,
        "vlozhenie": samoych_eur + notarialni_eur,
        "pechalba": bh_novo_5["kapitalov_rezultat"],
        "pechalba_naem": bh_novo_5["natrupen_naem"],
        "pechalba_poskapvane": bh_novo_5["kapitalov_rezultat"] - bh_novo_5["natrupen_naem"],
        "roi_pct": bh_novo_5["godishen_roi"],
        "srok_mes": 60,
        "risk": "Нисък",
        "detayli": {"noi": noi_novo, "cash_on_cash": coc_novo, "bh": bh_novo, "etap": etap},
    }

    strategii = [s1, s2, s3, s4, s5, s6, s7]

    # ═══════════════════════════════════════════════════
    # ДЕТАЙЛИ — 7 СТРАТЕГИИ
    # ═══════════════════════════════════════════════════

    for i, s in enumerate(strategii):
        risk_e = _risk_emoji(s["risk"])
        with st.expander(f"{s['ime']}  ·  ROI {s['roi_pct']:.1f}%/г  ·  Риск: {risk_e} {s['risk']}", expanded=(i == 3)):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.metric("Вложение", format_eur(s["vlozhenie"]))
            with c2:
                st.metric("Очаквана печалба", format_eur(s["pechalba"]))
            with c3:
                st.metric("ROI/г (CAGR)", format_pct(s["roi_pct"]))
            with c4:
                mes = s["srok_mes"]
                st.metric("Срок", f"{mes} мес. ({mes//12} год. {mes%12} мес.)" if mes > 0 else "Веднага")

            # Разбивка на печалбата: наем vs поскъпване
            pn = s.get("pechalba_naem", 0.0)
            pp = s.get("pechalba_poskapvane", s["pechalba"])
            if s["pechalba"] != 0:
                naem_share = round(pn / s["pechalba"] * 100)
                posk_share = 100 - naem_share
            else:
                naem_share = posk_share = 0
            ps1, ps2, ps3 = st.columns(3)
            with ps1:
                st.metric("Печалба от наем", format_eur(pn))
            with ps2:
                st.metric("Печалба от поскъпване", format_eur(pp))
            with ps3:
                st.metric("Дял наем / поскъпване", f"{naem_share}% / {posk_share}%")
            st.divider()

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
                    | ROI %/г (CAGR на equity) | {s['roi_pct']:.1f}% |
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
                    | ROI %/г (CAGR) | {s['roi_pct']:.1f}% |
                    """
                )

            elif i == 3:  # Наем
                mes_cf = det["mes_cf"]
                pb = det["payback"]
                god_razkhodi_mes = (
                    pokupna * (BUY_HOLD_OPERATIVNI_PCT["danuk_imot"] + BUY_HOLD_OPERATIVNI_PCT["zastrakhovka"]) / 12
                    + naem * DANUK_NAEM_PCT
                )
                naem_neto_mes = naem * (1 - BUY_HOLD_OPERATIVNI_PCT["vacancy"]) - god_razkhodi_mes
                st.markdown(
                    f"""
                    | Показател | Стойност |
                    |-----------|---------|
                    | Брутен месечен наем | {format_eur(naem)} |
                    | Vacancy (5%) | -{format_eur(naem * BUY_HOLD_OPERATIVNI_PCT['vacancy'])} |
                    | Данък имот (0.1%/год) | -{format_eur(pokupna * BUY_HOLD_OPERATIVNI_PCT['danuk_imot'] / 12)} |
                    | Застраховка (0.2%/год) | -{format_eur(pokupna * BUY_HOLD_OPERATIVNI_PCT['zastrakhovka'] / 12)} |
                    | Данък наем 9% | -{format_eur(naem * DANUK_NAEM_PCT)} |
                    | **Нетен наем/мес (NOI/12)** | **{format_eur(naem_neto_mes)}** |
                    | Месечна ипотека | {format_eur(det['vnоska'])} |
                    | NOI (годишен) | {format_eur(det['noi'])} |
                    | Cap Rate | {det['cap_rate']:.2f}% |
                    | Cash-on-Cash Return | {det['cash_on_cash']:.2f}% |
                    | Месечен паричен поток | {format_eur(det['mes_cf'])} |
                    | Срок за пълна възвр. | {f"{pb:.0f} мес. ({pb/12:.1f} год.)" if pb else "Отрицателен CF"} |
                    """
                )

                # Cap Rate оценка
                cr_val = det["cap_rate"]
                if cr_val >= 6:
                    st.success(f"✅ Cap Rate {cr_val:.2f}% — Отлична наемна доходност")
                elif cr_val >= 4:
                    st.warning(f"🟡 Cap Rate {cr_val:.2f}% — Приемлива наемна доходност. По-голямата част от печалбата идва от поскъпване.")
                else:
                    posk_pct = round((s4["pechalba_poskapvane"] / s4["pechalba"]) * 100) if s4["pechalba"] > 0 else 0
                    st.error(
                        f"🔴 Cap Rate {cr_val:.2f}% — Слаба наемна доходност. "
                        f"{posk_pct}% от печалбата идва от поскъпване, само {100 - posk_pct}% от наем. "
                        f"Тази стратегия е по-скоро залог на ценовия ръст, не на наемен доход."
                    )

                # Предупреждение за дълъг срок на възвращаемост
                if pb and pb > 240:
                    st.warning(
                        f"⚠️ Срок за пълна възвращаемост: **{pb:.0f} мес. ({pb/12:.1f} год.)** — над 20 години! "
                        f"Помисли дали наемният доход покрива рисковете при толкова дълъг хоризонт."
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
                # Разбивка наем/разходи
                bh_vn = det.get("mesechna_vnоska", 0)
                neto_mes = det.get("god_naem_neto", 0) / 12
                op_mes = det.get("operativni_razkhodi", 0) / 12
                bc1, bc2, bc3, bc4 = st.columns(4)
                bc1.metric("Брутен наем/мес", format_eur(det.get("mesecen_naem", naem)))
                bc2.metric("Разходи/мес", f"-{format_eur(op_mes)}")
                bc3.metric("Нетен наем/мес", format_eur(neto_mes),
                           delta=("Положителен" if neto_mes >= 0 else "ОТРИЦАТЕЛЕН"))
                bc4.metric("Месечна вноска", format_eur(bh_vn) if bh_vn > 0 else "100% собств.")

                st.markdown("**Прогноза по години:**")
                rows = []
                for g_data in det["po_godini"][1:]:
                    rows.append({
                        "Година": g_data["godina"],
                        "Стойност имот": format_eur(g_data["stojnost_imot"]),
                        "Натрупан наем": format_eur(g_data["natrupen_naem"]),
                        "Остатък кредит": format_eur(g_data["ostatok_kredit"]),
                        "Капиталов резултат": format_eur(g_data["kapitalov_rezultat"]),
                        "CAGR %/г": format_pct(g_data["godishen_roi"]),
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

            elif i == 6:  # Ново стр-во — готов
                bh_det = det["bh"]
                # Разбивка наем/разходи
                bh7_vn = bh_det.get("mesechna_vnоska", 0)
                neto7_mes = bh_det.get("god_naem_neto", 0) / 12
                op7_mes = bh_det.get("operativni_razkhodi", 0) / 12
                s7c1, s7c2, s7c3, s7c4 = st.columns(4)
                s7c1.metric("Брутен наем/мес", format_eur(bh_det.get("mesecen_naem", naem)))
                s7c2.metric("Разходи/мес", f"-{format_eur(op7_mes)}")
                s7c3.metric("Нетен наем/мес", format_eur(neto7_mes),
                            delta=("Положителен" if neto7_mes >= 0 else "ОТРИЦАТЕЛЕН"))
                s7c4.metric("Месечна вноска", format_eur(bh7_vn) if bh7_vn > 0 else "100% собств.")

                st.markdown("**Buy & Hold прогноза (5 год.):**")
                rows = []
                for g_data in bh_det["po_godini"][1:6]:
                    rows.append({
                        "Година": g_data["godina"],
                        "Стойност имот": format_eur(g_data["stojnost_imot"]),
                        "Натрупан наем": format_eur(g_data["natrupen_naem"]),
                        "Остатък кредит": format_eur(g_data["ostatok_kredit"]),
                        "Капиталов резултат": format_eur(g_data["kapitalov_rezultat"]),
                        "CAGR %/г": format_pct(g_data["godishen_roi"]),
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                st.caption(
                    f"Cash-on-Cash (само наем): {det['cash_on_cash']:.2f}%/г  ·  "
                    f"Етап: {det['etap']}"
                )

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
            "Наем €": f"{s.get('pechalba_naem', 0):,.0f}",
            "Поскъпване €": f"{s.get('pechalba_poskapvane', s['pechalba']):,.0f}",
            "Обща печалба €": f"{s['pechalba']:,.0f}",
            "ROI %/г": f"{s['roi_pct']:.1f}%",
            "Срок (мес)": s["srok_mes"],
            "Риск": f"{_risk_emoji(s['risk'])} {s['risk']}",
            "Маркери": "  ".join(marks) if marks else "—",
        })

    st.dataframe(pd.DataFrame(tbl_rows), use_container_width=True, hide_index=True)
    st.caption("ROI %/г = годишна CAGR на вложения собствен капитал (поскъпване + наем)")

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
            text=[f"{s['roi_pct']:.1f}%/г" for s in strategii],
            textposition="outside",
        ))
        fig_roi.update_layout(
            **PLOTLY_DARK,
            title="ROI %/г по стратегии (CAGR)",
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

    # ── PDF ИЗТЕГЛЯНЕ ──────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col_pdf, _, _ = st.columns([1, 1, 1])
    with col_pdf:
        try:
            from utils.pdf_export import generate_report
            user_email = (st.session_state.user or {}).get("email", "")
            # Подготви списък стратегии за PDF
            strategii_pdf = [
                {"ime": s["ime"], "vlozhenie": s["vlozhenie"],
                 "pechalba": s["pechalba"], "roi_pct": s["roi_pct"],
                 "srok_mes": s["srok_mes"], "risk": s["risk"]}
                for s in strategii
            ]
            pdf_bytes = generate_report(
                profil=dict(profil),
                imot=dict(im),
                strategii=strategii_pdf,
                najdobra_strategia=preporyaka.get("najdobra_strategia"),
                user_email=user_email,
            )
            filename = f"Real_Mentor_Analiz_{date.today()}.pdf"
            st.download_button(
                label="📄  Изтегли пълния анализ като PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.caption(f"PDF грешка: {e}")

    # ═══════════════════════════════════════════════════
    # ЗАПАЗИ КАЛКУЛАЦИЯ
    # ═══════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 💾 Запази тази калкулация")

    user = st.session_state.user
    if user:
        save_name = st.text_input(
            "Наименование",
            key="save_calc_name",
            placeholder=f"напр. Апартамент {im.get('grad', '')} {int(im.get('cena', 0) / 1000)}к",
            help="Дай кратко описание за лесно намиране по-късно",
        )

        col_save, col_info = st.columns([1, 2])
        with col_save:
            if st.button("💾  Запази калкулацията", use_container_width=True):
                if not save_name.strip():
                    st.error("Въведи наименование.")
                else:
                    results_dict = {
                        "roi_pct": препоръчана_стр["roi_pct"],
                        "pechalba": препоръчана_стр["pechalba"],
                        "vlozhenie": препоръчана_стр["vlozhenie"],
                        "srok_mes": препоръчана_стр["srok_mes"],
                    }
                    with st.spinner("Запазва се..."):
                        calc_id, err = save_calculation(
                            user_id=user["id"],
                            name=save_name.strip(),
                            property_data=dict(im),
                            results=results_dict,
                            strategy=препоръчана_стр["ime"],
                        )
                    if calc_id:
                        st.success(f"Запазено! Виж в 📋 Моите имоти.")
                    else:
                        st.error(f"Грешка: {err}")
        with col_info:
            st.markdown(
                '<p style="color:#6b7280;font-size:0.8rem;margin-top:0.5rem">'
                'Запазената калкулация ще се появи в <strong style="color:#c9a84c">Моите имоти</strong>, '
                'откъдето можеш да я заредиш отново или да добавиш бележки.</p>',
                unsafe_allow_html=True,
            )
    else:
        st.info("Влез в акаунта си, за да запазваш калкулации.")

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("✅  Продължи към Чеклист за покупка", type="primary", use_container_width=True):
            st.session_state.page = "checklist"
            st.rerun()
