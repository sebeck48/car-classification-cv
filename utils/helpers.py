"""
helpers.py — маленькі утиліти, що не вписуються в інші модулі.
"""

import os
from config import ALLOWED_IMAGE_EXTENSIONS


def is_valid_image_path(path: str) -> bool:
    """Перевіряє що шлях веде до існуючого файлу з дозволеним розширенням."""
    if not os.path.isfile(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    return ext in ALLOWED_IMAGE_EXTENSIONS


def format_confidence(confidence: float) -> str:
    """Форматує впевненість у відсоток. 0.934 → '93.4%'."""
    return f"{confidence * 100:.1f}%"
