"""Страница 2 — Профил на инвеститора."""
from __future__ import annotations
from datetime import date
import streamlit as st
from utils.calculations import kreditен_kapacitet
from utils.recommendation import preporycha_strategia, profil_preporyaka_tekst
from utils.styles import format_eur, format_pct, badge
from utils.market_data import GRADOVE, LIHVA_DEFAULT


def render():
    # Auto-load saved profile from Supabase once per session
    user = st.session_state.get("user")
    if user and not st.session_state.get("profil_loaded"):
        from utils.database import load_profile
        saved, err = load_profile(user["id"])
        if saved and not err:
            st.session_state.profil = {**st.session_state.profil, **saved}
        st.session_state.profil_loaded = True

    p = st.session_state.profil

    st.markdown('<p class="page-indicator">СТЪПКА 1</p>', unsafe_allow_html=True)
    st.markdown("# 👤 Профил на инвеститора")
    st.markdown(
        '<p style="color:#9ca3af">Въведи финансовите си данни — изчисляваме кредитния ти капацитет и персонална препоръка.</p>',
        unsafe_allow_html=True,
    )

    # ── СЕКЦИЯ А: ДОХОДИ ─────────────────────────────────────────────────────
    st.markdown("### 💰 Доходи и разходи")
    col1, col2, col3 = st.columns(3)

    with col1:
        p["neto_zaplata"] = st.number_input(
            "Нетна заплата (€/мес)",
            min_value=0.0, max_value=50000.0, step=100.0,
            value=float(p["neto_zaplata"]),
            help="Твоят нетен (след данъци) месечен доход",
        )
        p["partnyor_dohod"] = st.number_input(
            "Доход на партньор (€/мес)",
            min_value=0.0, max_value=50000.0, step=100.0,
            value=float(p["partnyor_dohod"]),
        )
        p["drugi_dohodi"] = st.number_input(
            "Допълнителни доходи (€/мес)",
            min_value=0.0, max_value=50000.0, step=50.0,
            value=float(p["drugi_dohodi"]),
            help="Наеми, фрийланс, дивиденти и т.н.",
        )

    with col2:
        p["mesechni_razkhodi"] = st.number_input(
            "Месечни разходи (€/мес)",
            min_value=0.0, max_value=20000.0, step=50.0,
            value=float(p["mesechni_razkhodi"]),
            help="Наем, храна, транспорт, комунални, абонаменти",
        )
        p["tekushti_krediti"] = st.number_input(
            "Текущи кредитни вноски (€/мес)",
            min_value=0.0, max_value=10000.0, step=50.0,
            value=float(p["tekushti_krediti"]),
            help="Потребителски кредити, коли, студентски и т.н.",
        )
        p["target_cash_flow"] = st.number_input(
            "Желан месечен паричен поток (€)",
            min_value=0.0, max_value=10000.0, step=50.0,
            value=float(p["target_cash_flow"]),
            help="Колко допълнителни приходи искаш от имота (0 = не е приоритет)",
        )

    with col3:
        p["spestyavane_cash"] = st.number_input(
            "Спестявания / наличен кеш (€)",
            min_value=0.0, max_value=2000000.0, step=1000.0,
            value=float(p["spestyavane_cash"]),
            help="Общо налично за инвестиция",
        )

    # ── СЕКЦИЯ Б: ИНВЕСТИЦИОННИ ЦЕЛИ ─────────────────────────────────────────
    st.markdown("### 🎯 Инвестиционни цели")
    col1, col2, col3 = st.columns(3)

    with col1:
        p["horiont"] = st.selectbox(
            "Инвестиционен хоризонт",
            ["Краткосрочен (1-3 год.)", "Средносрочен (3-7 год.)", "Дългосрочен (7+ год.)"],
            index=["Краткосрочен (1-3 год.)", "Средносрочен (3-7 год.)", "Дългосрочен (7+ год.)"].index(p["horiont"]),
        )
    with col2:
        p["risk"] = st.selectbox(
            "Рисков толеранс",
            ["Нисък", "Среден", "Висок"],
            index=["Нисък", "Среден", "Висок"].index(p["risk"]),
        )
    with col3:
        p["grad"] = st.selectbox(
            "Целеви град",
            GRADOVE,
            index=GRADOVE.index(p["grad"]) if p["grad"] in GRADOVE else 0,
        )

    st.session_state.profil = p

    # ── ЗАПАЗВАНЕ НА ПРОФИЛА ──────────────────────────────────────────────────
    st.markdown("---")
    user = st.session_state.get("user")
    if user:
        if st.button("💾 Запамети профила", type="secondary"):
            from utils.database import save_profile
            ok, err = save_profile(user["id"], dict(p))
            if ok:
                st.success("✅ Профилът е запазен успешно!")
            else:
                st.error(f"❌ Грешка при запазване: {err}")
        st.caption("Профилът ти се запазва в облака. При следващо влизане данните ще се заредят автоматично.")
    else:
        st.info("🔒 Влез в акаунта си, за да запазиш профила в облака.")

    # ── ИЗЧИСЛЕНИЯ ────────────────────────────────────────────────────────────
    kap = kreditен_kapacitet(
        neto_dohod=p["neto_zaplata"],
        partnyor_dohod=p["partnyor_dohod"],
        drugi_dohodi=p["drugi_dohodi"],
        mesechni_razkhodi=p["mesechni_razkhodi"],
        tekushti_krediti=p["tekushti_krediti"],
        samoychastie_pct=0.20,
    )

    # ── РЕЗЮМЕ КАРТА ──────────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("### 📋 Твоят инвестиционен потенциал")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Общ месечен доход",
            format_eur(kap["obshto_dohod"]),
        )
    with c2:
        st.metric(
            "Свободна сума/мес",
            format_eur(kap["svobodna_suma"]),
            delta=f"Макс вноска: {format_eur(kap['max_vnоska'])}",
        )
    with c3:
        st.metric(
            "Максимален кредит",
            format_eur(kap["max_kredit"]),
            help="При 25 год. и 2.5% лихва",
        )
    with c4:
        st.metric(
            "Максимален имот",
            format_eur(kap["max_imot"]),
            delta=f"Самоучастие: {format_eur(kap['nujno_samoychastie'])}",
        )

    # Потенциал карта
    total_potencial = kap["max_imot"]

    if total_potencial > 0:
        potencial_color = "#c9a84c" if total_potencial >= 80000 else "#fc8181"
        st.markdown(
            f"""
            <div class="rm-card" style="text-align:center;padding:1.5rem">
                <p style="color:#9ca3af;font-size:0.85rem;margin:0 0 0.25rem 0">ТВОЯТ ИНВЕСТИЦИОНЕН ПОТЕНЦИАЛ</p>
                <p style="color:{potencial_color};font-size:2.5rem;font-weight:700;margin:0">
                    {format_eur(total_potencial)}
                </p>
                <p style="color:#9ca3af;font-size:0.8rem;margin:0.25rem 0 0 0">
                    максимална стойност на имот при 20% самоучастие
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.warning("Свободната сума е твърде ниска за ипотечен кредит. Провери разходите и доходите.")

    # ── ПРЕПОРЪКА ─────────────────────────────────────────────────────────────
    st.markdown("### 🧭 Персонална препоръка")

    preporyaka = preporycha_strategia(
        risk_tolerans=p["risk"],
        investicionen_horiont=p["horiont"],
        svoboden_cash=p["spestyavane_cash"],
        mesecen_cash_flow_nujda=p["target_cash_flow"],
        etap="Акт 16 (готов нов)",
        max_imot=kap["max_imot"],
    )

    tekst = profil_preporyaka_tekst(
        risk_tolerans=p["risk"],
        investicionen_horiont=p["horiont"],
        svoboden_cash=p["spestyavane_cash"],
        mesecen_cash_flow=p["target_cash_flow"],
    )

    if preporyaka["najdobra_strategia"]:
        naj = preporyaka["najdobra_strategia"]
        st.markdown(
            f"""
            <div class="rm-card" style="border-left:4px solid #c9a84c">
                <p style="color:#c9a84c;font-size:0.75rem;font-weight:700;margin:0 0 0.25rem 0">ПРЕПОРЪЧАНА СТРАТЕГИЯ</p>
                <h3 style="margin:0 0 0.5rem 0;color:#e8eaf0">{naj['ime']}</h3>
                <p style="color:#9ca3af;font-size:0.85rem;margin:0">{naj['pricina']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(tekst)

    # Всички стратегии
    if preporyaka["vsichki_strategii"]:
        with st.expander("Виж всички препоръки по приоритет"):
            for i, s in enumerate(preporyaka["vsichki_strategii"]):
                rank = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
                st.markdown(f"**{rank} {s['ime']}** — {s['pricina']}")

    # ── CTA + PDF ─────────────────────────────────────────────────────────────
    st.markdown("---")
    col_btn, col_pdf, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("➡️  Продължи към Оценка на имот", type="primary", use_container_width=True):
            st.session_state.page = "imot"
            st.rerun()
    with col_pdf:
        try:
            from utils.pdf_export import generate_report
            user_email = (st.session_state.user or {}).get("email", "")
            pdf_bytes = generate_report(
                profil=dict(p),
                imot=dict(st.session_state.imot),
                user_email=user_email,
            )
            filename = f"Real_Mentor_Analiz_{date.today()}.pdf"
            st.download_button(
                label="📄  Изтегли анализа като PDF",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.caption(f"PDF грешка: {e}")
