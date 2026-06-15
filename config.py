"""
config.py — центральний файл з усіма налаштуваннями проєкту.
Усі «магічні числа» та шляхи зберігаються тут, щоб
легко змінювати їх в одному місці.
"""

import os

# ── Базовий шлях проєкту ──────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Налаштування моделі ───────────────────────────────────────────────────────
MODEL_CONFIG = {
    "weights_path": os.path.join(BASE_DIR, "model", "weights", "efficientnet_cars.pth"),

    # B2 точніший за B0, але повільніший. Варіанти: b0, b2, b3
    # b0 → image_size 224 | b2 → 260 | b3 → 300
    "efficientnet_version": "efficientnet_b2",
    "image_size": 260,

    "num_classes": 35,
    "confidence_threshold": 0.2,

    # Test Time Augmentation: усереднює N передбачень з різними аугментаціями
    # Точніше, але повільніше. 1 = вимкнено
    "tta_steps": 5,
}

# ── Налаштування бази даних ───────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "port":     5432,
    "database": "car_recognition",
    "user":     "postgres",
    "password": "12345678",   # ← ЗМІНИ на свій пароль
}

# ── Налаштування GUI ──────────────────────────────────────────────────────────
GUI_CONFIG = {
    "window_title": "Розпізнавання автомобілів",
    "window_width":  1000,
    "window_height":  680,

    # Максимальний розмір прев'ю зображення у вікні (пікселі)
    "preview_max_width":  520,
    "preview_max_height": 400,

    # Кольорова схема
    "bg_color":      "#1e1e2e",   # темний фон
    "accent_color":  "#89b4fa",   # синій акцент
    "text_color":    "#cdd6f4",   # світлий текст
    "success_color": "#a6e3a1",   # зелений — висока впевненість
    "warning_color": "#f9e2af",   # жовтий — низька впевненість
}

# ── Розширення файлів зображень, які дозволені до завантаження ────────────────
ALLOWED_IMAGE_EXTENSIONS = (
    ".jpg", ".jpeg",
    ".png",
    ".bmp",
    ".webp",
)
