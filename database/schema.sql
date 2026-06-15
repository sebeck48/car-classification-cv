-- schema.sql — схема бази даних для проєкту розпізнавання авто.
-- Запусти цей файл один раз у pgAdmin або через psql:
--   psql -U postgres -d car_recognition -f schema.sql

-- ── Таблиця марок автомобілів ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS brands (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,  -- назва марки, напр. "Toyota"
    country     VARCHAR(100),                  -- країна виробника
    founded     INTEGER                        -- рік заснування
);

-- ── Таблиця моделей автомобілів ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS car_models (
    id              SERIAL PRIMARY KEY,
    brand_id        INTEGER NOT NULL REFERENCES brands(id) ON DELETE CASCADE,
    model_name      VARCHAR(150) NOT NULL,     -- напр. "Camry"
    generation      VARCHAR(50),               -- напр. "XV70"
    year_start      INTEGER,                   -- перший рік випуску
    year_end        INTEGER,                   -- останній рік (NULL = досі випускається)
    body_type       VARCHAR(50),               -- sedan, suv, hatchback...
    engine_volume   DECIMAL(3,1),              -- об'єм двигуна у літрах
    horsepower      INTEGER,                   -- потужність у к.с.
    description     TEXT,                      -- короткий опис

    -- Мітка класу, яку видає наша модель (напр. "toyota_camry_2018")
    class_label     VARCHAR(200) UNIQUE
);

-- ── Індекс для швидкого пошуку по class_label ─────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_car_models_class_label
    ON car_models(class_label);

-- ── Тестові дані (кілька прикладів) ───────────────────────────────────────────
INSERT INTO brands (name, country, founded) VALUES
    ('Toyota',  'Японія',    1937),
    ('BMW',     'Німеччина', 1916),
    ('Ford',    'США',       1903),
    ('Honda',   'Японія',    1948),
    ('Mercedes-Benz', 'Німеччина', 1926)
ON CONFLICT (name) DO NOTHING;

INSERT INTO car_models
    (brand_id, model_name, generation, year_start, year_end,
     body_type, engine_volume, horsepower, description, class_label)
VALUES
    (1, 'Camry',   'XV70', 2017, NULL,  'sedan', 2.5, 203,
     'Флагманський седан Toyota середнього класу.',
     'Toyota Camry 2018'),

    (1, 'Corolla', 'E210', 2018, NULL,  'sedan', 1.8, 140,
     'Найпопулярніший автомобіль у світі.',
     'Toyota Corolla 2019'),

    (2, '3 Series', 'G20', 2018, NULL,  'sedan', 2.0, 255,
     'Культовий спортивний седан BMW.',
     'BMW 3 Series 2019'),

    (3, 'Mustang', 'S550', 2014, NULL,  'coupe', 5.0, 450,
     'Легендарне американське спортивне купе.',
     'Ford Mustang 2015'),

    (4, 'Civic',  'FK',   2015, 2021,  'sedan', 1.5, 174,
     'Компактний седан Honda з турбодвигуном.',
     'Honda Civic 2016')
ON CONFLICT (class_label) DO NOTHING;
