"""
main.py — точка входу. Запускай цей файл командою:
    python main.py

Що відбувається при запуску:
  1. Підключаємось до PostgreSQL
  2. Отримуємо список класів з БД
  3. Ініціалізуємо модель EfficientNet
  4. Завантажуємо навчені ваги (якщо є)
  5. Запускаємо Tkinter вікно
"""

import os
import tkinter as tk
import sys

from config import MODEL_CONFIG, BASE_DIR
from database.db_manager import DatabaseManager
from model.classifier import CarClassifier
from gui.app import CarRecognitionApp


def load_class_labels_from_file() -> list[str] | None:
    """Читає мітки класів з файлу що створюється після тренування."""
    labels_path = os.path.join(BASE_DIR, "model", "weights", "class_labels.txt")
    if not os.path.exists(labels_path):
        return None
    with open(labels_path, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def main():
    # ── Крок 1: Підключення до бази даних ────────────────────────────────────
    print("Підключення до бази даних...")
    db = DatabaseManager()
    db.connect()

    if not db.is_connected():
        print("ПОМИЛКА: не вдалося підключитись до PostgreSQL.")
        print("Перевір налаштування в config.py (DB_CONFIG).")
        sys.exit(1)

    # ── Крок 2: Отримуємо список класів ──────────────────────────────────────
    # Пріоритет: файл після тренування → БД → заглушка
    class_labels = load_class_labels_from_file()

    if class_labels:
        print(f"Мітки класів завантажено з файлу: {len(class_labels)} класів")
    else:
        class_labels = db.get_all_class_labels()
        if class_labels:
            print(f"Мітки класів завантажено з БД: {len(class_labels)} класів")
        else:
            print("ПОПЕРЕДЖЕННЯ: мітки класів не знайдено. Використовую заглушку.")
            class_labels = [f"class_{i}" for i in range(MODEL_CONFIG["num_classes"])]

    # ── Крок 3: Ініціалізація моделі ─────────────────────────────────────────
    print("Ініціалізація моделі EfficientNet...")
    classifier = CarClassifier(class_labels=class_labels)

    # ── Крок 4: Завантаження навчених ваг (необов'язково для першого запуску) ─
    classifier.load_weights()   # виведе попередження якщо файл не знайдено

    # ── Крок 5: Запуск GUI ────────────────────────────────────────────────────
    print("Запуск інтерфейсу...")
    root = tk.Tk()

    app = CarRecognitionApp(
        root=root,
        classifier=classifier,
        db=db,
    )

    # Закриття вікна — відключаємо БД
    def on_close():
        db.disconnect()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


if __name__ == "__main__":
    main()
