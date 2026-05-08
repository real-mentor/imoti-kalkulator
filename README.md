# Real Mentor — Имотен Калкулатор

Калкулатор за имотни инвестиции в България. Изграден с Streamlit + Supabase.

## Стартиране локално

```bash
cd ~/Desktop/imoti-kalkulator-v2
venv/bin/streamlit run app.py
```

---

## Автоматично обновяване на цени

### Ръчно пускане от твоя Mac (препоръчително)

imot.bg блокира GitHub Actions IP адреси (стандартна anti-bot защита).
За реални актуализирани цени — пускай скрипта **локално**:

```bash
cd ~/Desktop/imoti-kalkulator-v2
source venv/bin/activate
python admin/update_prices.py
```

Скриптът:
- **Фаза 1** (винаги): записва всички baseline цени от `utils/locations.py` в Supabase
- **Фаза 2** (от твоя Mac): scrape-ва 22 квартала от imot.bg и обновява с реални цени

Препоръчвам да го пускаш веднъж месечно (около 9-то число).

### GitHub Actions (автоматично на 9-то число)

Workflow-ът се пуска автоматично, но най-вероятно **Фаза 2 ще fail-не** поради IP блокиране.
Това е нормално — Фаза 1 (baseline) ще се изпълни успешно и exit кодът е 0.
GitHub **няма да изпрати** email нотификация при scraping failure.
Email нотификация ще получиш само ако Supabase е недостъпен.

### Как работи скриптът

1. Изтегля начална страница на imot.bg за cookies и сесия
2. Ротира между 3 различни User-Agent headers
3. За всеки квартал: fetch SEO URL → decode Windows-1251 → парсва `div.item`
4. Извлича EUR цена от `div.price > div` и кв.м от `div.info`
5. Изчислява median €/кв.м от всички обяви
6. Upsert в Supabase таблица `market_prices`

### Как работи
3. Записва резултатите в Supabase таблица `market_prices`
4. При неуспех — запазва baseline стойностите от `utils/locations.py`

**Кога се пуска:** автоматично на **9-то число всеки месец** в 11:00 ч. (08:00 UTC)

**При неуспех:** GitHub изпраща email нотификация автоматично.

---

## Настройка на GitHub Actions (Стъпка по стъпка)

### СТЪПКА 1 — Създай GitHub профил и repo

1. Отиди на [github.com](https://github.com) → **Sign up** (ако нямаш профил)
2. Влез и натисни зеления бутон **New** (горе вляво)
3. Попълни:
   - **Repository name:** `imoti-kalkulator`
   - **Visibility:** Private ← важно, за да не се вижда .env и кодът
   - НЕ слагай отметка на "Add README"
4. Натисни **Create repository**
5. GitHub показва страница с инструкции — запази URL-то на repo-то (изглежда като `https://github.com/ТВОЕТО_ИМЕ/imoti-kalkulator`)

---

### СТЪПКА 2 — Качи кода в GitHub

Отвори терминал в папката на проекта и изпълни:

```bash
cd ~/Desktop/imoti-kalkulator-v2

# Свържи локалния repo с GitHub (смени URL-то с твоето!)
git remote add origin https://github.com/ТВОЕТО_ИМЕ/imoti-kalkulator.git

# Добави всички файлове (без venv и .env — те са в .gitignore)
git add .
git commit -m "Initial commit — Real Mentor app"

# Качи в GitHub
git push -u origin main
```

> Ако Git пита за потребителско име и парола — въведи GitHub имейл и **Personal Access Token**  
> (не паролата за GitHub!). Как се прави токен: GitHub → Settings → Developer settings → Personal access tokens → Generate new token → избери `repo` права)

---

### СТЪПКА 3 — Добави SUPABASE_URL и SUPABASE_KEY като GitHub Secrets

> Secrets са криптирани — никой не може да ги види, дори ти след като ги запишеш.

1. Отвори твоя GitHub repo
2. Натисни **Settings** (горе вдясно в repo страницата)
3. В лявото меню → **Secrets and variables** → **Actions**
4. Натисни **New repository secret** и добави:

   | Name | Value |
   |------|-------|
   | `SUPABASE_URL` | `https://XXXXX.supabase.co` (от .env файла) |
   | `SUPABASE_KEY` | `eyJhbGci...` (service_role key от Supabase) |

> **Важно:** Използвай **service_role** key (не anon key), за да може скриптът да пише в таблицата.  
> Намери го в: Supabase → Project Settings → API → `service_role` key

---

### СТЪПКА 4 — Изпълни миграцията за market_prices таблицата

1. Отвори [supabase.com](https://supabase.com) → твоя проект → **SQL Editor**
2. Copy/paste съдържанието на `migrations/002_market_prices.sql`
3. Натисни **Run**

---

### СТЪПКА 5 — Провери че Actions работи

**Тест веднага (ръчно пускане):**
1. В GitHub repo → натисни таба **Actions**
2. Вляво виждаш "Обновяване на пазарни цени"
3. Натисни **Run workflow** → **Run workflow** (зеленият бутон)
4. Изчакай ~2-3 минути и провери дали е зелено (✅) или червено (❌)
5. Натисни върху run-а → виж логовете

**Ако е червено:**
- Провери дали Secrets са добавени правилно
- Провери дали миграцията е изпълнена в Supabase
- Логовете ще покажат точно къде е проблемът

**Автоматично:** На 9-то число следващия месец Actions ще се пусне сам.  
Ако fail-не → ще получиш email от GitHub на адреса с който си регистриран.

---

## Структура на проекта

```
imoti-kalkulator-v2/
├── app.py                    # Главен файл
├── views/                    # Страниците
│   ├── page_home.py
│   ├── page_profil.py
│   ├── page_imot.py          # Оценка на имот
│   ├── page_strategii.py     # 7 стратегии
│   ├── page_moite_imoti.py   # Запазени калкулации
│   ├── page_checklist.py
│   ├── page_remont.py
│   ├── page_settings.py
│   └── page_auth.py
├── utils/
│   ├── locations.py          # 48 града, 88+ квартала
│   ├── market_data.py        # Пазарни данни и коефициенти
│   ├── calculations.py       # Финансови формули
│   ├── styles.py             # CSS тема
│   ├── database.py           # Supabase CRUD
│   └── ...
├── admin/
│   ├── update_prices.py      # Скрипт за обновяване на цени
│   └── requirements.txt
├── migrations/
│   ├── 001_create_tables.sql # profiles + saved_calculations
│   └── 002_market_prices.sql # market_prices таблица
├── .github/
│   └── workflows/
│       └── update_prices.yml # GitHub Actions workflow
├── .env                      # НЕ се качва в GitHub!
├── .gitignore
└── requirements.txt
```
