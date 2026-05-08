"""Страница за вход и регистрация."""
from __future__ import annotations
import streamlit as st
from utils.database import register, login, load_profile


def render():
    # Центриран layout
    _, col, _ = st.columns([1, 1.4, 1])

    with col:
        st.markdown(
            """
            <div style="text-align:center;padding:2rem 0 1.5rem 0">
                <p style="font-size:2.5rem;margin:0">🏠</p>
                <h1 style="color:#c9a84c;font-size:1.8rem;margin:0.25rem 0 0 0">Real Mentor</h1>
                <p style="color:#9ca3af;font-size:0.9rem;margin:0.25rem 0 0 0">
                    Калкулатор за имотни инвестиции в България
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        tab_vhod, tab_reg = st.tabs(["🔑  Вход", "✨  Регистрация"])

        # ── ТАБ ВХОД ──────────────────────────────────────────
        with tab_vhod:
            st.markdown("<br>", unsafe_allow_html=True)

            email_in = st.text_input(
                "Имейл адрес",
                key="login_email",
                placeholder="example@mail.com",
            )
            password_in = st.text_input(
                "Парола",
                type="password",
                key="login_password",
                placeholder="••••••••",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("🔑  Влез в акаунта", type="primary", use_container_width=True):
                if not email_in or not password_in:
                    st.error("Попълни имейл и парола.")
                else:
                    with st.spinner("Влизаш..."):
                        user, err = login(email_in.strip(), password_in)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.user = user
                        # Зареди профила от Supabase
                        profile_data, _ = load_profile(user["id"])
                        if profile_data:
                            st.session_state.profil.update(profile_data)
                        st.success("Добре дошъл!")
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                '<p style="color:#6b7280;font-size:0.75rem;text-align:center">'
                'Нямаш акаунт? Отвори таба <strong style="color:#c9a84c">Регистрация</strong>.</p>',
                unsafe_allow_html=True,
            )

        # ── ТАБ РЕГИСТРАЦИЯ ────────────────────────────────────
        with tab_reg:
            st.markdown("<br>", unsafe_allow_html=True)

            email_reg = st.text_input(
                "Имейл адрес",
                key="reg_email",
                placeholder="example@mail.com",
            )
            password_reg = st.text_input(
                "Парола",
                type="password",
                key="reg_password",
                placeholder="Минимум 6 символа",
            )
            password_reg2 = st.text_input(
                "Потвърди паролата",
                type="password",
                key="reg_password2",
                placeholder="••••••••",
            )

            gdpr = st.checkbox(
                "Съгласен съм с обработката на лични данни",
                key="reg_gdpr",
            )
            st.markdown(
                '<p style="color:#6b7280;font-size:0.72rem;margin-top:-0.5rem">'
                'Съхраняваме само имейл и твоите калкулации. '
                'Можеш да изтриеш акаунта си по всяко време от Настройки.</p>',
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)

            if st.button("✨  Създай акаунт", type="primary", use_container_width=True):
                if not email_reg or not password_reg or not password_reg2:
                    st.error("Попълни всички полета.")
                elif password_reg != password_reg2:
                    st.error("Паролите не съвпадат.")
                elif len(password_reg) < 6:
                    st.error("Паролата трябва да е поне 6 символа.")
                elif not gdpr:
                    st.error("Трябва да се съгласиш с обработката на данни.")
                else:
                    with st.spinner("Регистриране..."):
                        user, err = register(email_reg.strip(), password_reg)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.user = user
                        st.success("Акаунтът е създаден! Добре дошъл в Real Mentor.")
                        st.rerun()

        # Footer
        st.markdown(
            '<p style="color:#374151;font-size:0.7rem;text-align:center;margin-top:2rem">'
            'Real Mentor · 2026 · Данните са защитени с Supabase RLS</p>',
            unsafe_allow_html=True,
        )
