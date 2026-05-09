"""Страница 1 — Начало."""
from __future__ import annotations
import streamlit as st
from utils.styles import DARK_THEME_CSS


def render():
    st.markdown(
        '<p class="page-indicator">Real Mentor · Имотен Калкулатор</p>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <h1 style="font-size:2.2rem;margin-bottom:0.25rem">
            Анализ на имотни инвестиции
        </h1>
        <p style="color:#9ca3af;font-size:1.05rem;margin-bottom:2rem">
            Програма <strong style="color:#c9a84c">Real Mentor — От 0 до Първия Имот</strong>
        </p>
        """,
        unsafe_allow_html=True,
    )

    # Описание
    st.markdown(
        """
        <div class="rm-card">
        <p style="color:#e8eaf0;font-size:0.95rem;line-height:1.7;margin:0">
            Инструментът изчислява и сравнява <strong style="color:#c9a84c">7 инвестиционни стратегии</strong>
            за всеки конкретен имот в България — от покупка на зелено до Fix &amp; Flip и Buy &amp; Hold.
            Всички пазарни данни са актуализирани за <strong>Q1 2026</strong>.
            Въведи своя профил и имота, който разглеждаш — получаваш персонална препоръка за секунди.
        </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Карти за страниците
    cards = [
        {
            "icon": "👤",
            "title": "Профил на инвеститора",
            "desc": "Въведи доходи, спестявания и цели. Изчисляваме кредитния ти капацитет и препоръчваме стратегия.",
            "page": "profil",
            "badge": "СТЪПКА 1",
            "badge_v": "gold",
        },
        {
            "icon": "🏗️",
            "title": "Оценка на имот",
            "desc": "Въведи имота — получаваш пазарна справка, сравнение с подобни обяви и вход за анализ на стратегии.",
            "page": "imot",
            "badge": "СТЪПКА 2",
            "badge_v": "gold",
        },
        {
            "icon": "📊",
            "title": "Сравнение на 7 стратегии",
            "desc": "Ядрото на инструмента. Виж ROI, риск и срок за всяка стратегия. Разбираш коя е най-добра за теб.",
            "page": "strategii",
            "badge": "ЯДРО",
            "badge_v": "blue",
        },
        {
            "icon": "✅",
            "title": "Чеклист за покупка",
            "desc": "7 етапа юридическа проверка. Интерактивен чеклист — отбелязвай изпълнените стъпки.",
            "page": "checklist",
            "badge": "ЗАЩИТА",
            "badge_v": "green",
        },
        {
            "icon": "🔨",
            "title": "График за ремонт",
            "desc": "Gantt chart за 8 седмици ремонт. Чеклист по фази, схема на плащане 30/30/30/10.",
            "page": "remont",
            "badge": "ИЗПЪЛНЕНИЕ",
            "badge_v": "green",
        },
    ]

    col1, col2 = st.columns(2)
    cols = [col1, col2]

    for i, card in enumerate(cards):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="rm-card" style="min-height:150px">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.75rem">
                        <span style="font-size:1.8rem">{card['icon']}</span>
                        <span class="rm-badge rm-badge-{card['badge_v']}">{card['badge']}</span>
                    </div>
                    <h3 style="margin:0 0 0.4rem 0;font-size:1rem;color:#e8eaf0">{card['title']}</h3>
                    <p style="color:#9ca3af;font-size:0.85rem;margin:0;line-height:1.6">{card['desc']}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button(f"Отвори {card['title']}", key=f"home_btn_{card['page']}", use_container_width=True):
                st.session_state.page = card["page"]
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")

    # Статистики
    st.markdown(
        """
        <h3 style="margin-bottom:1rem">Пазарни данни — Q1 2026</h3>
        """,
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.metric("София", "~2 400 €/кв.м", "+16% vs 2024")
    with m2:
        st.metric("Варна", "~1 919 €/кв.м", "+12% vs 2024")
    with m3:
        st.metric("Пловдив", "~1 212 €/кв.м", "+10% vs 2024")
    with m4:
        st.metric("Бургас", "~1 766 €/кв.м", "+11% vs 2024")
    with m5:
        st.metric("Ипотека", "~2.5%/год.", "Най-ниско в ЕС")

    st.markdown("<br>", unsafe_allow_html=True)

    # CTA бутон
    col_cta, _, _ = st.columns([1, 1, 1])
    with col_cta:
        if st.button("🚀  Започни — Въведи профила си", type="primary", use_container_width=True):
            st.session_state.page = "profil"
            st.rerun()
