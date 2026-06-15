"""
download_images.py — автоматично завантажує додаткові фото для кожного класу.

Читає class_labels.txt, для кожного авто шукає фото в Bing
і зберігає у відповідну папку train/.

Запуск:
    python tools/download_images.py

Скільки фото завантажувати (IMAGES_PER_CLASS):
    50  — швидко, невелике покращення
    100 — оптимально (~15-20 хв)
    150 — найкраще, але довго
"""

import os
import sys
import shutil
from bing_image_downloader import downloader

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_DIR

# ── Налаштування ──────────────────────────────────────────────────────────────
IMAGES_PER_CLASS = 50        # скільки нових фото завантажити на клас
TRAIN_DIR        = os.path.join(BASE_DIR, "data", "car_data", "train")
LABELS_FILE      = os.path.join(BASE_DIR, "model", "weights", "class_labels.txt")
TEMP_DIR         = os.path.join(BASE_DIR, "data", "_download_temp")


def load_labels() -> list[str]:
    with open(LABELS_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def download_for_class(class_name: str, target_dir: str):
    """Завантажує фото для одного класу і переміщує у правильну папку."""

    # Пошуковий запит: назва авто + "car" для кращих результатів
    query = f"{class_name} car"

    print(f"\n  Завантаження: {class_name}")

    try:
        downloader.download(
            query,
            limit           = IMAGES_PER_CLASS,
            output_dir      = TEMP_DIR,
            adult_filter_off= True,
            force_replace   = False,
            timeout         = 10,
            verbose         = False,
        )
    except Exception as e:
        print(f"  Помилка завантаження: {e}")
        return 0

    # Bing зберігає у папку з назвою запиту — переміщуємо у train/
    query_dir = os.path.join(TEMP_DIR, query)
    if not os.path.exists(query_dir):
        return 0

    os.makedirs(target_dir, exist_ok=True)

    # Переміщуємо файли та перейменовуємо щоб не перезаписати існуючі
    existing = len(os.listdir(target_dir))
    moved = 0

    for filename in os.listdir(query_dir):
        src = os.path.join(query_dir, filename)
        ext = os.path.splitext(filename)[1].lower()
        if ext not in {".jpg", ".jpeg", ".png"}:
            continue
        dst = os.path.join(target_dir, f"bing_{existing + moved:05d}{ext}")
        try:
            shutil.move(src, dst)
            moved += 1
        except Exception:
            pass

    # Прибираємо тимчасову папку
    shutil.rmtree(query_dir, ignore_errors=True)
    return moved


def main():
    if not os.path.exists(LABELS_FILE):
        print("ПОМИЛКА: не знайдено class_labels.txt")
        print("Спочатку запусти тренування: python model/train.py")
        return

    labels = load_labels()
    print(f"Класів для завантаження: {len(labels)}")
    print(f"Фото на клас: {IMAGES_PER_CLASS}")
    print(f"Орієнтовний час: ~{len(labels) * IMAGES_PER_CLASS // 60} хв\n")

    total_downloaded = 0

    for i, class_name in enumerate(labels, 1):
        target_dir = os.path.join(TRAIN_DIR, class_name)
        before = len([f for f in os.listdir(target_dir)
                      if os.path.isfile(os.path.join(target_dir, f))]) if os.path.exists(target_dir) else 0

        count = download_for_class(class_name, target_dir)
        total_downloaded += count

        after = before + count
        print(f"  [{i}/{len(labels)}] {class_name}: {before} → {after} фото (+{count})")

    # Прибираємо тимчасову папку повністю
    shutil.rmtree(TEMP_DIR, ignore_errors=True)

    print(f"\n{'='*50}")
    print(f"Завантажено всього: {total_downloaded} нових фото")
    print(f"Тепер перетренуй модель: python model/train.py")


if __name__ == "__main__":
    main()
