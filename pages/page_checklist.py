"""Страница 5 — Чеклист за покупка."""
from __future__ import annotations
import streamlit as st

CHECKLIST = [
    {
        "etap": "1. Предварителна подготовка",
        "items": [
            ("fin_01", "Определен е максималният бюджет (цена + данъци + нотариус + ремонт)", True),
            ("fin_02", "Предварително одобрение от банка (ако е с кредит)", True),
            ("fin_03", "Резервирани са средства за непредвидени разходи (мин. 3–5%)", True),
            ("fin_04", "Проверена е оценката на имота от банката", False),
            ("fin_05", "Изчислени са всички разходи по сделката", True),
            ("fin_06", "Дефинирани са задължителните критерии (квартал, площ, тип, етаж)", False),
            ("fin_07", "Планираното предназначение е ясно (лично/наем/препродажба)", False),
        ],
    },
    {
        "etap": "2. Оглед и първоначална проверка",
        "items": [
            ("og_01", "Поискан е Акт 16 / Разрешение за ползване", True),
            ("og_02", "Проверена е данъчната оценка на имота", True),
            ("og_03", "Поискана е схема на апартамента от Кадастъра", True),
            ("og_04", "Проверен е сертификат за енергийна ефективност (клас A–G)", False),
            ("og_05", "Направен е оглед в различно часово (шум, осветление, трафик)", False),
            ("og_06", "Проверено е физическото съответствие с документите", True),
            ("og_07", "Справка в Агенция по вписванията — ипотеки, възбрани, тежести", True),
            ("og_08", "Проверка на веригата на собствеността (мин. 10 год.)", True),
        ],
    },
    {
        "etap": "3. Юридическа проверка (Дю Дилиджънс)",
        "items": [
            ("yu_01", "Нотариален акт на продавача — оригинал", True),
            ("yu_02", "Всички предходни нотариални актове (мин. 10 год.)", True),
            ("yu_03", "Удостоверение за вещни тежести от Агенция по вписванията", True),
            ("yu_04", "При наследствен имот: удостоверение за наследници", True),
            ("yu_05", "Проверка за съсобственост — всички трябва да подпишат", True),
            ("yu_06", "Акт 16 / Разрешение за ползване — оригинал", True),
            ("yu_07", "Технически паспорт на сградата (задълж. от 2009 г.)", False),
            ("yu_08", "Справка в съдебния регистър за дела срещу продавача", True),
            ("yu_09", "Проверка при Частен съдебен изпълнител", True),
        ],
    },
    {
        "etap": "4. Предварителен договор",
        "items": [
            ("pd_01", "Точно описание на имота (идентификатор по Кадастъра, площ)", True),
            ("pd_02", "Договорена реална продажна цена (не данъчна оценка)", True),
            ("pd_03", "Капаро и условия за задържане/връщане (стандартно 10%)", True),
            ("pd_04", "Начин и срок на плащане — точно описано", True),
            ("pd_05", "Краен срок за нотариален акт (конкретна дата)", True),
            ("pd_06", "Клауза за правно и физическо съответствие", True),
            ("pd_07", "Условие: одобрение на ипотечен кредит (право за отказ)", False),
        ],
    },
    {
        "etap": "5. Финансиране и банков кредит",
        "items": [
            ("kr_01", "Сравнени са минимум 3 банки (лихва, такси, условия)", False),
            ("kr_02", "Извършена е оценка от лицензиран оценител", True),
            ("kr_03", "Получено е писмено одобрение за кредит", True),
            ("kr_04", "Прочетен е ЦЕЛИЯТ договор за ипотечен кредит", True),
            ("kr_05", "Проверена е задължителната застраховка 'Живот'/'Имущество'", False),
        ],
    },
    {
        "etap": "6. Нотариален акт",
        "items": [
            ("na_01", "Последна проверка в АВ — в деня преди/в деня на сделката", True),
            ("na_02", "Нотариалният акт е прочетен ИЗЦЯЛО", True),
            ("na_03", "Проверени са всички данни: имена, ЕГН, адрес, площ, цена", True),
            ("na_04", "Парите са платени по уговорения начин (пред нотариуса)", True),
            ("na_05", "Получен е оригинален екземпляр на нотариалния акт", True),
        ],
    },
    {
        "etap": "7. Вписване и действия след сделката",
        "items": [
            ("vs_01", "Нотариалният акт е подаден за вписване ВЕДНАГА", True),
            ("vs_02", "Проверено е успешното вписване (imot.icsi.eu)", True),
            ("vs_03", "Декларирана е промяна пред Общината (2-месечен срок)", True),
            ("vs_04", "Прехвърлени са партиди: ЧЕЗ/EVN, ВиК, Топлофикация", True),
            ("vs_05", "Сключена е застраховка 'Имущество'", False),
            ("vs_06", "Декларирано е в НАП (ако имотът се наема)", False),
        ],
    },
]

TOTAL_ITEMS = sum(len(e["items"]) for e in CHECKLIST)
ZADYLZITELNI = sum(1 for e in CHECKLIST for (k, t, z) in e["items"] if z)


def render():
    st.markdown('<p class="page-indicator">ЗАЩИТА</p>', unsafe_allow_html=True)
    st.markdown("# ✅ Чеклист за покупка на имот")
    st.markdown(
        '<p style="color:#9ca3af">Следвай стъпките в реда, в който са наредени. '
        'Отбелязвай само когато действието е РЕАЛНО извършено. '
        '<span style="color:#fc8181">🔴 = Задължително</span></p>',
        unsafe_allow_html=True,
    )

    # Инициализация на чеклист state
    if "checklist_state" not in st.session_state:
        st.session_state.checklist_state = {k: False for e in CHECKLIST for (k, t, z) in e["items"]}

    ck = st.session_state.checklist_state
    completed = sum(1 for v in ck.values() if v)
    pct = completed / TOTAL_ITEMS * 100 if TOTAL_ITEMS > 0 else 0

    # Прогрес бар
    st.markdown(
        f"""
        <div style="margin-bottom:1.5rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:0.3rem">
                <span style="color:#9ca3af;font-size:0.85rem">Прогрес: {completed}/{TOTAL_ITEMS} изпълнени</span>
                <span style="color:#c9a84c;font-weight:600">{pct:.0f}%</span>
            </div>
            <div class="rm-progress-bar">
                <div class="rm-progress-fill" style="width:{pct}%"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Бутон за нулиране
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("✅ Отбележи всички", use_container_width=True):
            for k in ck:
                ck[k] = True
            st.rerun()
    with col2:
        if st.button("↩️ Нулирай", use_container_width=True):
            for k in ck:
                ck[k] = False
            st.rerun()

    st.markdown("---")

    # Чеклист по етапи
    for etap_data in CHECKLIST:
        etap_keys = [k for (k, t, z) in etap_data["items"]]
        etap_done = sum(1 for k in etap_keys if ck.get(k, False))
        etap_total = len(etap_keys)
        etap_pct = etap_done / etap_total * 100 if etap_total > 0 else 0

        etap_color = "#48bb78" if etap_done == etap_total else "#c9a84c" if etap_pct > 0 else "#6b7280"

        with st.expander(
            f"{'✅' if etap_done == etap_total else '🔄' if etap_pct > 0 else '⬜'}  {etap_data['etap']}  ·  {etap_done}/{etap_total}",
            expanded=(etap_pct > 0 and etap_pct < 100),
        ):
            for (key, tekst, zadylzhitelno) in etap_data["items"]:
                col_chk, col_txt = st.columns([0.06, 0.94])
                with col_chk:
                    ck[key] = st.checkbox("", value=ck.get(key, False), key=f"chk_{key}")
                with col_txt:
                    label_color = "#e8eaf0" if ck.get(key, False) else "#9ca3af"
                    zadylzh_badge = ' <span style="color:#fc8181;font-size:0.7rem;font-weight:700">ЗАДЪЛ.</span>' if zadylzhitelno else ""
                    strikethrough = "text-decoration:line-through;opacity:0.6;" if ck.get(key, False) else ""
                    st.markdown(
                        f'<p style="color:{label_color};{strikethrough}margin:0;padding:0.15rem 0;font-size:0.9rem">'
                        f'{tekst}{zadylzh_badge}</p>',
                        unsafe_allow_html=True,
                    )

    # 7 Задължителни
    st.markdown("---")
    st.markdown(
        """
        <div class="rm-card" style="border-left:4px solid #fc8181">
            <h3 style="color:#fc8181;margin:0 0 1rem 0">⚠️ 7 Задължителни проверки преди ВСЯКА сделка</h3>
            <ol style="color:#e8eaf0;line-height:2;margin:0;padding-left:1.2rem">
                <li>АВ проверка за тежести, ипотеки и възбрани</li>
                <li>Акт 16 / Разрешение за ползване — оригинал</li>
                <li>Всички съсобственици участват или са дали нотариално съгласие</li>
                <li>Нотариалният акт е прегледан от адвокат преди подписване</li>
                <li>Данъкът придобиване е платен преди нотариалния акт</li>
                <li>Последна проверка в АВ в деня на сделката</li>
                <li>Вписването е извършено ВЕДНАГА след нотариалния акт</li>
            </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="rm-card" style="border-left:4px solid #ecc94b">
            <h3 style="color:#ecc94b;margin:0 0 0.75rem 0">🧾 Ориентировъчни разходи по сделката</h3>
            <table style="width:100%;color:#e8eaf0;font-size:0.85rem;border-collapse:collapse">
                <tr style="border-bottom:1px solid #2d3151">
                    <td style="padding:6px 0"><strong>Данък придобиване</strong></td>
                    <td style="padding:6px 0;color:#c9a84c">2–3% от стойността</td>
                    <td style="padding:6px 0;color:#9ca3af">Купувач</td>
                </tr>
                <tr style="border-bottom:1px solid #2d3151">
                    <td style="padding:6px 0"><strong>Нотариална такса</strong></td>
                    <td style="padding:6px 0;color:#c9a84c">~0.1–1.5%</td>
                    <td style="padding:6px 0;color:#9ca3af">Купувач</td>
                </tr>
                <tr style="border-bottom:1px solid #2d3151">
                    <td style="padding:6px 0"><strong>Такса вписване</strong></td>
                    <td style="padding:6px 0;color:#c9a84c">~0.1%</td>
                    <td style="padding:6px 0;color:#9ca3af">Купувач</td>
                </tr>
                <tr style="border-bottom:1px solid #2d3151">
                    <td style="padding:6px 0"><strong>Адвокат</strong></td>
                    <td style="padding:6px 0;color:#c9a84c">300–2 000 лв.</td>
                    <td style="padding:6px 0;color:#9ca3af">Купувач</td>
                </tr>
                <tr>
                    <td style="padding:6px 0"><strong style="color:#fc8181">ОБЩО</strong></td>
                    <td style="padding:6px 0;color:#fc8181;font-weight:700">4–8%</td>
                    <td style="padding:6px 0;color:#9ca3af">Планирай буфер!</td>
                </tr>
            </table>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.checklist_state = ck

    st.markdown("<br>", unsafe_allow_html=True)
    col_btn, _, _ = st.columns([1, 1, 1])
    with col_btn:
        if st.button("🔨  Продължи към Ремонт", type="primary", use_container_width=True):
            st.session_state.page = "remont"
            st.rerun()
