"""Страница — Настройки и GDPR."""
from __future__ import annotations
import streamlit as st
from utils.database import change_password, delete_account


def render():
    user = st.session_state.user
    if not user:
        st.error("Трябва да си логнат.")
        return

    st.markdown('<p class="page-indicator">АКАУНТ</p>', unsafe_allow_html=True)
    st.markdown("# ⚙️ Настройки")

    # ── ИНФОРМАЦИЯ ЗА АКАУНТА ─────────────────────────────────
    st.markdown("### 👤 Акаунт")
    st.markdown(
        f"""
        <div class="rm-card">
            <p style="color:#9ca3af;font-size:0.75rem;margin:0">ИМЕЙЛ АДРЕС</p>
            <p style="color:#e8eaf0;font-size:1rem;font-weight:600;margin:0">{user.get('email', '—')}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ── ПРОМЯНА НА ПАРОЛА ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🔑 Промяна на парола")

    new_pass = st.text_input("Нова парола", type="password", placeholder="Минимум 6 символа", key="new_pass")
    new_pass2 = st.text_input("Потвърди новата парола", type="password", placeholder="••••••••", key="new_pass2")

    if st.button("🔑  Смени паролата", use_container_width=False):
        if not new_pass or not new_pass2:
            st.error("Попълни и двете полета.")
        elif new_pass != new_pass2:
            st.error("Паролите не съвпадат.")
        elif len(new_pass) < 6:
            st.error("Паролата трябва да е поне 6 символа.")
        else:
            with st.spinner("Записва се..."):
                ok, err = change_password(new_pass)
            if ok:
                st.success("Паролата е сменена успешно.")
            else:
                st.error(err)

    # ── GDPR — ИЗТРИВАНЕ ─────────────────────────────────────
    st.markdown("---")
    st.markdown("### 🗑️ Изтриване на акаунт")

    st.markdown(
        """
        <div class="rm-card" style="border-left:4px solid #fc8181">
            <h4 style="color:#fc8181;margin:0 0 0.5rem 0">⚠️ Необратимо действие</h4>
            <p style="color:#9ca3af;font-size:0.85rem;margin:0;line-height:1.6">
                При изтриване на акаунта <strong style="color:#e8eaf0">всички твои данни ще бъдат
                изтрити безвъзвратно</strong> — профил, запазени калкулации и бележки.
                Това действие не може да бъде отменено.
            </p>
            <p style="color:#9ca3af;font-size:0.8rem;margin:0.5rem 0 0 0">
                В съответствие с GDPR (Регламент ЕС 2016/679) имаш право да поискаш
                пълно изтриване на личните си данни.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    confirm = st.checkbox(
        "Разбирам, че всички данни ще бъдат изтрити безвъзвратно",
        key="gdpr_confirm",
    )

    if confirm:
        st.markdown(
            '<p style="color:#fc8181;font-size:0.85rem">Въведи имейла си за потвърждение:</p>',
            unsafe_allow_html=True,
        )
        confirm_email = st.text_input(
            "Потвърди имейл",
            key="confirm_email",
            placeholder=user.get("email", ""),
            label_visibility="collapsed",
        )

        if st.button(
            "🗑️  ИЗТРИЙ АКАУНТА МИ ЗАВИНАГИ",
            type="primary",
            use_container_width=False,
            key="delete_account_btn",
        ):
            if confirm_email.strip() != user.get("email", ""):
                st.error("Имейлът не съвпада. Въведи точния си имейл.")
            else:
                with st.spinner("Изтриване на всички данни..."):
                    ok, err = delete_account(user["id"])
                if ok:
                    st.session_state.user = None
                    st.session_state.page = "home"
                    st.success("Акаунтът и всички данни са изтрити.")
                    st.rerun()
                else:
                    st.error(f"Грешка: {err}")
