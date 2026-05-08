-- Таблица за автоматично обновявани пазарни цени
-- Пуска се от GitHub Actions на 9-то число всеки месец

CREATE TABLE IF NOT EXISTS public.market_prices (
    id           UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    grad         VARCHAR(100) NOT NULL,
    kvartal      VARCHAR(200) NOT NULL,
    avg_sqm      INTEGER      NOT NULL CHECK (avg_sqm > 0),
    listings_count INTEGER    DEFAULT 0,
    source       VARCHAR(50)  DEFAULT 'imot.bg',
    scraped_at   TIMESTAMPTZ  DEFAULT now(),

    UNIQUE (grad, kvartal)   -- upsert по тези две полета
);

-- Индекс за бързо четене по град
CREATE INDEX IF NOT EXISTS idx_market_prices_grad
    ON public.market_prices (grad);

-- RLS: само authenticated потребители могат да четат
ALTER TABLE public.market_prices ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Всички логнати могат да четат цени"
    ON public.market_prices
    FOR SELECT
    TO authenticated
    USING (true);

-- Само service_role (GitHub Actions) може да пише
-- (SUPABASE_KEY в GitHub Secrets трябва да е service_role key, не anon key)
CREATE POLICY "Service role може да пише цени"
    ON public.market_prices
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Коментар
COMMENT ON TABLE public.market_prices IS
    'Автоматично обновявани средни цени от imot.bg. GitHub Actions → admin/update_prices.py';
