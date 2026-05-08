"""Страница — Моите имоти (запазени калкулации)."""
from __future__ import annotations
import streamlit as st
from utils.database import load_calculations, delete_calculation, save_note
from utils.styles import format_eur, format_pct


def render():
    user = st.session_state.user
    if not user:
        st.error("Трябва да си логнат.")
        return

    st.markdown('<p class="page-indicator">МОИ ДАННИ</p>', unsafe_allow_html=True)
    st.markdown("# 📋 Моите имоти")
    st.markdown(
        '<p style="color:#9ca3af">Всички твои запазени калкулации. '
        'Кликни върху калкулация за да я заредиш отново.</p>',
        unsafe_allow_html=True,
    )

    # Зареди калкулациите
    calcs, err = load_calculations(user["id"])

    if err:
        st.error(f"Грешка при зареждане: {err}")
        return

    if not calcs:
        st.markdown(
            """
            <div class="rm-card" style="text-align:center;padding:3rem">
                <p style="font-size:2rem;margin:0">📭</p>
                <h3 style="color:#9ca3af;margin:0.5rem 0">Нямаш запазени калкулации</h3>
                <p style="color:#6b7280;font-size:0.85rem">
                    Отиди на <strong>Оценка на имот</strong> → <strong>Стратегии</strong>
                    и натисни "💾 Запази тази калкулация"
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🏗️  Оцени имот", type="primary"):
            st.session_state.page = "imot"
            st.rerun()
        return

    st.markdown(f"**{len(calcs)}** запазени калкулации")
    st.markdown("---")

    for calc in calcs:
        prop = calc.get("property_data", {})
        res  = calc.get("results", {})
        created = calc.get("created_at", "")[:10]

        roi  = res.get("roi_pct", 0)
        grad = prop.get("grad", "—")
        cena = prop.get("cena", 0)

        with st.expander(
            f"🏠  {calc['name']}  ·  {grad}  ·  {format_eur(cena)}  ·  {created}",
            expanded=False,
        ):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Цена", format_eur(cena))
            with col2:
                st.metric("Площ", f"{prop.get('kvadraturi', 0):.0f} кв.м")
            with col3:
                st.metric("ROI", format_pct(roi))
            with col4:
                st.metric("Стратегия", calc.get("strategy", "—"))

            # Детайли
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(
                    f"**Град:** {grad}  \n"
                    f"**Зона:** {prop.get('zona', '—')}  \n"
                    f"**Етап:** {prop.get('etap', '—')}  \n"
                    f"**Наем:** {format_eur(prop.get('ochakvаn_naem', 0))}/мес"
                )
            with col_b:
                st.markdown(
                    f"**Самоучастие:** {prop.get('samoychastie_pct', 0)*100:.0f}%  \n"
                    f"**Лихва:** {prop.get('lihva', 0)*100:.2f}%  \n"
                    f"**Срок:** {prop.get('srok_god', 0)} год.  \n"
                    f"**Запазено:** {created}"
                )

            # Бележки
            st.markdown("**📝 Бележки:**")
            note_key = f"note_{calc['id']}"
            if note_key not in st.session_state:
                st.session_state[note_key] = calc.get("notes", "")

            new_note = st.text_area(
                "Бележки",
                value=st.session_state[note_key],
                key=f"ta_{calc['id']}",
                label_visibility="collapsed",
                placeholder="Добави бележки за този имот...",
                height=80,
            )

            btn1, btn2, btn3 = st.columns(3)

            with btn1:
                if st.button("💾 Запази бележка", key=f"savenote_{calc['id']}", use_container_width=True):
                    ok, err2 = save_note(user["id"], calc["id"], new_note)
                    if ok:
                        st.session_state[note_key] = new_note
                        st.success("Бележката е запазена.")
                    else:
                        st.error(err2)

            with btn2:
                if st.button("📂 Зареди в Оценка", key=f"load_{calc['id']}", use_container_width=True):
                    # Зареди property_data в session state
                    if prop:
                        st.session_state.imot.update(prop)
                    st.session_state.page = "imot"
                    st.success(f"Заредено: {calc['name']}")
                    st.rerun()

            with btn3:
                if st.button("🗑️ Изтрий", key=f"del_{calc['id']}", use_container_width=True):
                    ok, err2 = delete_calculation(user["id"], calc["id"])
                    if ok:
                        st.success("Калкулацията е изтрита.")
                        st.rerun()
                    else:
                        st.error(err2)
