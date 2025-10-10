-- Таблица: public.www_data_idx
CREATE TABLE IF NOT EXISTS public.www_data_idx
(
    id integer PRIMARY KEY,
    mask character varying(20),
    name_rus character varying(100),
    name_eng character varying(100),
    source character varying(50),
    url character varying(200),
    descr character varying(50),
    date_upd TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица: public.health_monitor
CREATE TABLE IF NOT EXISTS public.health_monitor
(
    id numeric PRIMARY KEY,
    date_upd TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    health_status numeric,
    add_text character varying(200),
    color character varying(100)
);

-- Таблица: public.agriculture_moex
CREATE TABLE IF NOT EXISTS public.agriculture_moex
(
    id_value numeric,
    date_val date,
    min_val numeric,
    max_val numeric,
    avg_val numeric,
    volume numeric,
    currency character varying(20),
    date_upd TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (id_value, date_val)
);

-- Начальные данные для health_monitor
INSERT INTO public.health_monitor (id, health_status, add_text) 
VALUES (1012, 100, '') 
ON CONFLICT (id) DO NOTHING;

-- Создание последовательности для www_data_idx
CREATE SEQUENCE IF NOT EXISTS www_data_idx_id_seq;
ALTER TABLE public.www_data_idx ALTER COLUMN id SET DEFAULT nextval('www_data_idx_id_seq');

-- Вставляем реальные данные из CSV
INSERT INTO public.www_data_idx (id, mask, name_rus, name_eng, source, url, descr, date_upd) VALUES
(25, NULL, 'Пшеница протеин 12,5%', 'WHFOB', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(26, NULL, 'Ячмень', 'BRFOB', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(27, NULL, 'Кукуруза', 'CRFOB', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(28, NULL, 'Масло подсолнечное', 'SOEXP', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(29, NULL, 'Шрот подсолнечный', 'SMEXP', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(31, NULL, 'Сахар ПФО', 'SUGAROTCVOL', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(32, NULL, 'Сахар ЦФО', 'SUGAROTCCEN', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(33, NULL, 'Сахар ЮФО', 'SUGAROTCSOU', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(30, NULL, 'Соя DAP Курская область', 'SOYDK', 'MOEX', 'https://iss.moex.com/iss/history/engines/stock/markets/index/securities/', NULL, '2023-11-02'),
(225, NULL, 'Железная руда 62% Fe', 'FEFZ23', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-11'),
(150, NULL, 'Железная руда 62% Fe', 'FEFF24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, NULL),
(178, NULL, 'Железная руда 62% Fe', 'FEFG24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(179, NULL, 'Железная руда 62% Fe', 'FEFH24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(180, NULL, 'Железная руда 62% Fe', 'FEFJ24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(181, NULL, 'Железная руда 62% Fe', 'FEFK24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(182, NULL, 'Железная руда 62% Fe', 'FEFM24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(183, NULL, 'Железная руда 62% Fe', 'FEFN24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(184, NULL, 'Железная руда 62% Fe', 'FEFQ24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(185, NULL, 'Железная руда 62% Fe', 'FEFU24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(186, NULL, 'Железная руда 62% Fe', 'FEFV24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(187, NULL, 'Железная руда 62% Fe', 'FEFX24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(188, NULL, 'Железная руда 62% Fe', 'FEFZ24', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(189, NULL, 'Железная руда 62% Fe', 'FEFF25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(190, NULL, 'Железная руда 62% Fe', 'FEFG25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(191, NULL, 'Железная руда 62% Fe', 'FEFH25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(192, NULL, 'Железная руда 62% Fe', 'FEFJ25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(193, NULL, 'Железная руда 62% Fe', 'FEFK25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(194, NULL, 'Железная руда 62% Fe', 'FEFM25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(195, NULL, 'Железная руда 62% Fe', 'FEFN25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(196, NULL, 'Железная руда 62% Fe', 'FEFQ25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(197, NULL, 'Железная руда 62% Fe', 'FEFU25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(198, NULL, 'Железная руда 62% Fe', 'FEFV25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(199, NULL, 'Железная руда 62% Fe', 'FEFX25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(200, NULL, 'Железная руда 62% Fe', 'FEFZ25', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(201, NULL, 'Железная руда 62% Fe', 'FEFF26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(202, NULL, 'Железная руда 62% Fe', 'FEFG26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(203, NULL, 'Железная руда 62% Fe', 'FEFH26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(204, NULL, 'Железная руда 62% Fe', 'FEFJ26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(205, NULL, 'Железная руда 62% Fe', 'FEFK26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(206, NULL, 'Железная руда 62% Fe', 'FEFM26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(207, NULL, 'Железная руда 62% Fe', 'FEFN26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(208, NULL, 'Железная руда 62% Fe', 'FEFQ26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(209, NULL, 'Железная руда 62% Fe', 'FEFU26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(210, NULL, 'Железная руда 62% Fe', 'FEFV26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(211, NULL, 'Железная руда 62% Fe', 'FEFX26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(212, NULL, 'Железная руда 62% Fe', 'FEFZ26', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(213, NULL, 'Железная руда 62% Fe', 'FEFF27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(214, NULL, 'Железная руда 62% Fe', 'FEFG27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(215, NULL, 'Железная руда 62% Fe', 'FEFH27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(216, NULL, 'Железная руда 62% Fe', 'FEFJ27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(217, NULL, 'Железная руда 62% Fe', 'FEFK27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(218, NULL, 'Железная руда 62% Fe', 'FEFM27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(219, NULL, 'Железная руда 62% Fe', 'FEFN27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(220, NULL, 'Железная руда 62% Fe', 'FEFQ27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(221, NULL, 'Железная руда 62% Fe', 'FEFU27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(222, NULL, 'Железная руда 62% Fe', 'FEFV27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(223, NULL, 'Железная руда 62% Fe', 'FEFX27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(224, NULL, 'Железная руда 62% Fe', 'FEFZ27', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2024-01-10'),
(229, NULL, 'Железная руда 62% Fe', 'FEFF28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-02-13'),
(230, NULL, 'Железная руда 62% Fe', 'FEFG28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-02-13'),
(231, NULL, 'Железная руда 62% Fe', 'FEFH28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-07-09'),
(232, NULL, 'Железная руда 62% Fe', 'FEFJ28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-07-09'),
(233, NULL, 'Железная руда 62% Fe', 'FEFK28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-07-09'),
(234, NULL, 'Железная руда 62% Fe', 'FEFM28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-07-09'),
(235, NULL, 'Железная руда 62% Fe', 'FEFN28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-07-09'),
(236, NULL, 'Железная руда 62% Fe', 'FEFQ28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-08-27'),
(237, NULL, 'Железная руда 62% Fe', 'FEFU28', 'ore_futures', 'https://api.sgx.com/derivatives/v1.0/history/symbol/', NULL, '2025-09-21')

ON CONFLICT (id) DO NOTHING;

-- Обновляем последовательность
SELECT setval('www_data_idx_id_seq', (SELECT MAX(id) FROM public.www_data_idx));

CREATE INDEX IF NOT EXISTS idx_agriculture_id_value ON agriculture_moex(id_value);
CREATE INDEX IF NOT EXISTS idx_www_data_source ON www_data_idx(source);
CREATE INDEX IF NOT EXISTS idx_agriculture_date_val ON agriculture_moex(date_val);