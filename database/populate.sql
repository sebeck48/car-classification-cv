-- populate.sql — заповнення БД реальними 35 класами з датасету
-- Запуск: виконується автоматично через PowerShell

-- Очищаємо старі тестові дані
TRUNCATE car_models, brands RESTART IDENTITY CASCADE;

-- ── Марки ─────────────────────────────────────────────────────────────────────
INSERT INTO brands (name, country, founded) VALUES
    ('Acura',           'США',        1986),
    ('Aston Martin',    'Велика Британія', 1913),
    ('Audi',            'Німеччина',   1909),
    ('Bentley',         'Велика Британія', 1919),
    ('BMW',             'Німеччина',   1916),
    ('Chevrolet',       'США',        1911),
    ('Dodge',           'США',        1900),
    ('FIAT',            'Італія',     1899),
    ('Ferrari',         'Італія',     1939),
    ('Ford',            'США',        1903),
    ('GMC',             'США',        1912),
    ('HUMMER',          'США',        1992),
    ('Honda',           'Японія',     1948),
    ('Hyundai',         'Південна Корея', 1967),
    ('Infiniti',        'Японія',     1989),
    ('Jeep',            'США',        1941),
    ('Lamborghini',     'Італія',     1963),
    ('Land Rover',      'Велика Британія', 1948),
    ('Mazda',           'Японія',     1920),
    ('Mercedes-Benz',   'Німеччина',   1926),
    ('Nissan',          'Японія',     1933),
    ('Porsche',         'Німеччина',   1931),
    ('Rolls-Royce',     'Велика Британія', 1906),
    ('Toyota',          'Японія',     1937),
    ('Volkswagen',      'Німеччина',   1937),
    ('Volvo',           'Швеція',     1927);

-- ── Моделі з точними class_label що збігаються з датасетом ───────────────────
INSERT INTO car_models
    (brand_id, model_name, year_start, year_end, body_type, engine_volume, horsepower, description, class_label)
VALUES
    ((SELECT id FROM brands WHERE name='Acura'),
     'TL Sedan', 2009, 2014, 'sedan', 3.5, 280,
     'Представницький седан Acura з V6 двигуном.',
     'Acura TL Sedan 2012'),

    ((SELECT id FROM brands WHERE name='Aston Martin'),
     'V8 Vantage Coupe', 2005, 2018, 'coupe', 4.7, 420,
     'Розкішне британське спортивне купе з V8 двигуном.',
     'Aston Martin V8 Vantage Coupe 2012'),

    ((SELECT id FROM brands WHERE name='Audi'),
     '100 Sedan', 1991, 1994, 'sedan', 2.8, 174,
     'Класичний представницький седан Audi 90-х років.',
     'Audi 100 Sedan 1994'),

    ((SELECT id FROM brands WHERE name='Audi'),
     'R8 Coupe', 2007, NULL, 'coupe', 5.2, 525,
     'Флагманський суперкар Audi з двигуном V10 посередині.',
     'Audi R8 Coupe 2012'),

    ((SELECT id FROM brands WHERE name='Audi'),
     'RS 4 Convertible', 2006, 2008, 'convertible', 4.2, 420,
     'Спортивний кабріолет Audi з потужним V8.',
     'Audi RS 4 Convertible 2008'),

    ((SELECT id FROM brands WHERE name='Bentley'),
     'Continental GT Coupe', 2003, NULL, 'coupe', 6.0, 560,
     'Ультрарозкішне купе Bentley з W12 двигуном.',
     'Bentley Continental GT Coupe 2012'),

    ((SELECT id FROM brands WHERE name='BMW'),
     'M3 Coupe', 2007, 2013, 'coupe', 4.0, 414,
     'Культове спортивне купе BMW з V8 двигуном серії E92.',
     'BMW M3 Coupe 2012'),

    ((SELECT id FROM brands WHERE name='BMW'),
     'X5 SUV', 2006, 2013, 'suv', 3.0, 300,
     'Преміальний позашляховик BMW другого покоління.',
     'BMW X5 SUV 2007'),

    ((SELECT id FROM brands WHERE name='Chevrolet'),
     'Malibu Hybrid Sedan', 2008, 2012, 'sedan', 2.4, 164,
     'Гібридний седан Chevrolet з комбінованою силовою установкою.',
     'Chevrolet Malibu Hybrid Sedan 2010'),

    ((SELECT id FROM brands WHERE name='Chevrolet'),
     'TrailBlazer SS', 2006, 2009, 'suv', 6.0, 395,
     'Потужна версія SS позашляховика TrailBlazer з V8.',
     'Chevrolet TrailBlazer SS 2009'),

    ((SELECT id FROM brands WHERE name='Dodge'),
     'Charger Sedan', 2011, NULL, 'sedan', 5.7, 370,
     'Легендарний американський м''язовий седан Dodge.',
     'Dodge Charger Sedan 2012'),

    ((SELECT id FROM brands WHERE name='FIAT'),
     '500 Abarth', 2012, NULL, 'hatchback', 1.4, 160,
     'Спортивна версія FIAT 500 від тюнінгового підрозділу Abarth.',
     'FIAT 500 Abarth 2012'),

    ((SELECT id FROM brands WHERE name='Ferrari'),
     '458 Italia Convertible', 2011, 2015, 'convertible', 4.5, 562,
     'Відкрита версія Ferrari 458 Italia — шедевр італійського інжинірингу.',
     'Ferrari 458 Italia Convertible 2012'),

    ((SELECT id FROM brands WHERE name='Ford'),
     'Expedition EL SUV', 2007, 2017, 'suv', 5.4, 300,
     'Повнорозмірний позашляховик Ford з подовженою базою.',
     'Ford Expedition EL SUV 2009'),

    ((SELECT id FROM brands WHERE name='Ford'),
     'Focus Sedan', 2005, 2007, 'sedan', 2.0, 136,
     'Компактний седан Ford Focus другого покоління.',
     'Ford Focus Sedan 2007'),

    ((SELECT id FROM brands WHERE name='Ford'),
     'Mustang Convertible', 2005, 2009, 'convertible', 4.0, 210,
     'Кабріолет Ford Mustang п''ятого покоління.',
     'Ford Mustang Convertible 2007'),

    ((SELECT id FROM brands WHERE name='GMC'),
     'Canyon Extended Cab', 2004, 2012, 'pickup', 2.9, 185,
     'Компактний пікап GMC Canyon з подовженою кабіною.',
     'GMC Canyon Extended Cab 2012'),

    ((SELECT id FROM brands WHERE name='HUMMER'),
     'H2 SUT Crew Cab', 2005, 2009, 'pickup', 6.0, 325,
     'Пікап-версія легендарного HUMMER H2.',
     'HUMMER H2 SUT Crew Cab 2009'),

    ((SELECT id FROM brands WHERE name='Honda'),
     'Accord Sedan', 2008, 2012, 'sedan', 2.4, 177,
     'Надійний середньокласовий седан Honda Accord.',
     'Honda Accord Sedan 2012'),

    ((SELECT id FROM brands WHERE name='Honda'),
     'Odyssey Minivan', 2011, 2017, 'minivan', 3.5, 248,
     'Сімейний мінівен Honda Odyssey четвертого покоління.',
     'Honda Odyssey Minivan 2012'),

    ((SELECT id FROM brands WHERE name='Hyundai'),
     'Elantra Sedan', 2006, 2010, 'sedan', 2.0, 138,
     'Компактний седан Hyundai Elantra четвертого покоління.',
     'Hyundai Elantra Sedan 2007'),

    ((SELECT id FROM brands WHERE name='Hyundai'),
     'Santa Fe SUV', 2010, 2012, 'suv', 2.4, 175,
     'Кросовер Hyundai Santa Fe другого покоління.',
     'Hyundai Santa Fe SUV 2012'),

    ((SELECT id FROM brands WHERE name='Infiniti'),
     'QX56 SUV', 2010, 2013, 'suv', 5.6, 400,
     'Флагманський повнорозмірний позашляховик Infiniti.',
     'Infiniti QX56 SUV 2011'),

    ((SELECT id FROM brands WHERE name='Jeep'),
     'Grand Cherokee SUV', 2011, NULL, 'suv', 3.6, 290,
     'Культовий американський позашляховик Jeep Grand Cherokee.',
     'Jeep Grand Cherokee SUV 2012'),

    ((SELECT id FROM brands WHERE name='Lamborghini'),
     'Diablo Coupe', 1990, 2001, 'coupe', 6.0, 492,
     'Легендарний суперкар Lamborghini Diablo — ікона 90-х.',
     'Lamborghini Diablo Coupe 2001'),

    ((SELECT id FROM brands WHERE name='Land Rover'),
     'Range Rover SUV', 2012, NULL, 'suv', 5.0, 510,
     'Флагманський преміальний позашляховик Land Rover четвертого покоління.',
     'Land Rover Range Rover SUV 2012'),

    ((SELECT id FROM brands WHERE name='Mazda'),
     'Tribute SUV', 2008, 2011, 'suv', 2.5, 171,
     'Компактний кросовер Mazda Tribute другого покоління.',
     'Mazda Tribute SUV 2011'),

    ((SELECT id FROM brands WHERE name='Mercedes-Benz'),
     '300-Class Convertible', 1992, 1993, 'convertible', 3.2, 228,
     'Розкішний кабріолет Mercedes-Benz серії W124.',
     'Mercedes-Benz 300-Class Convertible 1993'),

    ((SELECT id FROM brands WHERE name='Mercedes-Benz'),
     'Sprinter Van', 2010, NULL, 'van', 3.0, 190,
     'Комерційний фургон Mercedes-Benz Sprinter другого покоління.',
     'Mercedes-Benz Sprinter Van 2012'),

    ((SELECT id FROM brands WHERE name='Nissan'),
     'Juke Hatchback', 2010, 2019, 'hatchback', 1.6, 188,
     'Компактний кросовер Nissan Juke з турбованим двигуном.',
     'Nissan Juke Hatchback 2012'),

    ((SELECT id FROM brands WHERE name='Porsche'),
     'Panamera Sedan', 2009, NULL, 'sedan', 3.6, 300,
     'Чотиридверний спортивний седан Porsche Panamera.',
     'Porsche Panamera Sedan 2012'),

    ((SELECT id FROM brands WHERE name='Rolls-Royce'),
     'Phantom Drophead Coupe', 2007, NULL, 'convertible', 6.7, 453,
     'Найрозкішніший кабріолет у світі від Rolls-Royce.',
     'Rolls-Royce Phantom Drophead Coupe Convertible 2012'),

    ((SELECT id FROM brands WHERE name='Toyota'),
     'Camry Sedan', 2011, 2014, 'sedan', 2.5, 178,
     'Надійний середньокласовий седан Toyota Camry сьомого покоління.',
     'Toyota Camry Sedan 2012'),

    ((SELECT id FROM brands WHERE name='Volkswagen'),
     'Golf Hatchback', 2010, 2014, 'hatchback', 2.0, 200,
     'Популярний хетчбек Volkswagen Golf шостого покоління.',
     'Volkswagen Golf Hatchback 2012'),

    ((SELECT id FROM brands WHERE name='Volvo'),
     'C30 Hatchback', 2006, 2013, 'hatchback', 2.5, 227,
     'Стильний компактний хетчбек Volvo C30 з турбо двигуном.',
     'Volvo C30 Hatchback 2012');
