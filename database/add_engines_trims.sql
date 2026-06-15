-- Додаємо нові колонки до таблиці car_models
ALTER TABLE car_models ADD COLUMN IF NOT EXISTS engines TEXT;
ALTER TABLE car_models ADD COLUMN IF NOT EXISTS trims   TEXT;

-- Оновлюємо дані для всіх 35 класів
UPDATE car_models SET
    engines = '3.5L V6 (280 к.с.)',
    trims   = 'Base, Technology, A-SPEC'
WHERE class_label = 'Acura TL Sedan 2012';

UPDATE car_models SET
    engines = '4.7L V8 (420 к.с.)',
    trims   = 'Coupe, S, RS'
WHERE class_label = 'Aston Martin V8 Vantage Coupe 2012';

UPDATE car_models SET
    engines = '2.8L V6 (174 к.с.), 2.0L (115 к.с.)',
    trims   = 'C, CD, E'
WHERE class_label = 'Audi 100 Sedan 1994';

UPDATE car_models SET
    engines = '4.2L V8 (430 к.с.), 5.2L V10 (525 к.с.)',
    trims   = 'Base, Spyder, GT'
WHERE class_label = 'Audi R8 Coupe 2012';

UPDATE car_models SET
    engines = '4.2L V8 (420 к.с.)',
    trims   = 'Base, Quattro'
WHERE class_label = 'Audi RS 4 Convertible 2008';

UPDATE car_models SET
    engines = '6.0L W12 (560 к.с.), 4.0L V8 (500 к.с.)',
    trims   = 'Base, Speed, Supersports'
WHERE class_label = 'Bentley Continental GT Coupe 2012';

UPDATE car_models SET
    engines = '4.0L V8 (414 к.с.)',
    trims   = 'Base, Competition, DTM'
WHERE class_label = 'BMW M3 Coupe 2012';

UPDATE car_models SET
    engines = '3.0L (218 к.с.), 4.8L V8 (355 к.с.)',
    trims   = 'xDrive30i, xDrive48i, M Sport'
WHERE class_label = 'BMW X5 SUV 2007';

UPDATE car_models SET
    engines = '2.4L (164 к.с.)',
    trims   = 'Base Hybrid'
WHERE class_label = 'Chevrolet Malibu Hybrid Sedan 2010';

UPDATE car_models SET
    engines = '6.0L V8 (395 к.с.)',
    trims   = 'SS'
WHERE class_label = 'Chevrolet TrailBlazer SS 2009';

UPDATE car_models SET
    engines = '3.6L V6 (292 к.с.), 5.7L V8 (370 к.с.), 6.4L V8 (470 к.с.)',
    trims   = 'SE, SXT, R/T, SRT8'
WHERE class_label = 'Dodge Charger Sedan 2012';

UPDATE car_models SET
    engines = '1.4L турбо (160 к.с.)',
    trims   = 'Base, Esseesse'
WHERE class_label = 'FIAT 500 Abarth 2012';

UPDATE car_models SET
    engines = '4.5L V8 (562 к.с.)',
    trims   = 'Base, Spider'
WHERE class_label = 'Ferrari 458 Italia Convertible 2012';

UPDATE car_models SET
    engines = '5.4L V8 (300 к.с.)',
    trims   = 'XLT, Eddie Bauer, Limited'
WHERE class_label = 'Ford Expedition EL SUV 2009';

UPDATE car_models SET
    engines = '2.0L (136 к.с.), 2.3L (145 к.с.)',
    trims   = 'S, SE, SES, SEL'
WHERE class_label = 'Ford Focus Sedan 2007';

UPDATE car_models SET
    engines = '4.0L V6 (210 к.с.), 4.6L V8 (300 к.с.)',
    trims   = 'V6 Deluxe, GT, GT Premium'
WHERE class_label = 'Ford Mustang Convertible 2007';

UPDATE car_models SET
    engines = '2.9L (185 к.с.), 3.7L V8 (242 к.с.)',
    trims   = 'Base, SLE, SLT'
WHERE class_label = 'GMC Canyon Extended Cab 2012';

UPDATE car_models SET
    engines = '6.0L V8 (325 к.с.)',
    trims   = 'Base, Luxury'
WHERE class_label = 'HUMMER H2 SUT Crew Cab 2009';

UPDATE car_models SET
    engines = '2.4L (177 к.с.), 3.5L V6 (271 к.с.)',
    trims   = 'LX, EX, EX-L, Touring'
WHERE class_label = 'Honda Accord Sedan 2012';

UPDATE car_models SET
    engines = '3.5L V6 (248 к.с.)',
    trims   = 'LX, EX, EX-L, Touring'
WHERE class_label = 'Honda Odyssey Minivan 2012';

UPDATE car_models SET
    engines = '2.0L (138 к.с.)',
    trims   = 'GLS, SE, Limited'
WHERE class_label = 'Hyundai Elantra Sedan 2007';

UPDATE car_models SET
    engines = '2.4L (175 к.с.), 2.7L V6 (189 к.с.)',
    trims   = 'GLS, SE, Limited'
WHERE class_label = 'Hyundai Santa Fe SUV 2012';

UPDATE car_models SET
    engines = '5.6L V8 (400 к.с.)',
    trims   = 'Base, Premium, Theater'
WHERE class_label = 'Infiniti QX56 SUV 2011';

UPDATE car_models SET
    engines = '3.6L V6 (290 к.с.), 5.7L V8 (360 к.с.)',
    trims   = 'Laredo, Limited, Overland, SRT8'
WHERE class_label = 'Jeep Grand Cherokee SUV 2012';

UPDATE car_models SET
    engines = '5.7L V12 (492 к.с.), 6.0L V12 (530 к.с.)',
    trims   = 'Diablo, VT, SV, SE'
WHERE class_label = 'Lamborghini Diablo Coupe 2001';

UPDATE car_models SET
    engines = '5.0L V8 (375 к.с.), 5.0L SC V8 (510 к.с.)',
    trims   = 'Vogue, Sport, Autobiography, SV'
WHERE class_label = 'Land Rover Range Rover SUV 2012';

UPDATE car_models SET
    engines = '2.5L (171 к.с.)',
    trims   = 'Base, Sport, Grand Touring'
WHERE class_label = 'Mazda Tribute SUV 2011';

UPDATE car_models SET
    engines = '2.8L (197 к.с.), 3.2L (228 к.с.)',
    trims   = '300CE, 300TE'
WHERE class_label = 'Mercedes-Benz 300-Class Convertible 1993';

UPDATE car_models SET
    engines = '2.1L дизель (129 к.с.), 3.0L (190 к.с.)',
    trims   = 'Base, CDI, Standard, High Roof'
WHERE class_label = 'Mercedes-Benz Sprinter Van 2012';

UPDATE car_models SET
    engines = '1.6L турбо (188 к.с.)',
    trims   = 'S, SV, SL, Nismo'
WHERE class_label = 'Nissan Juke Hatchback 2012';

UPDATE car_models SET
    engines = '3.6L V6 (300 к.с.), 4.8L V8 (400 к.с.)',
    trims   = 'Base, 4S, Turbo, Turbo S'
WHERE class_label = 'Porsche Panamera Sedan 2012';

UPDATE car_models SET
    engines = '6.7L V12 (453 к.с.)',
    trims   = 'Base, Series II'
WHERE class_label = 'Rolls-Royce Phantom Drophead Coupe Convertible 2012';

UPDATE car_models SET
    engines = '2.5L (178 к.с.), 3.5L V6 (268 к.с.)',
    trims   = 'LE, SE, XSE, XLE, Hybrid'
WHERE class_label = 'Toyota Camry Sedan 2012';

UPDATE car_models SET
    engines = '2.0L турбо (200 к.с.), 2.5L (170 к.с.)',
    trims   = 'Trendline, Comfortline, Highline, GTI'
WHERE class_label = 'Volkswagen Golf Hatchback 2012';

UPDATE car_models SET
    engines = '2.5L турбо (227 к.с.)',
    trims   = 'Base, Kinetic, R-Design'
WHERE class_label = 'Volvo C30 Hatchback 2012';
