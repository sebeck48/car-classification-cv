"""
clean_dataset.py — видаляє пошкоджені та непридатні зображення з датасету.

Запуск:
    python tools/clean_dataset.py
"""

import os
import sys
from PIL import Image, ImageFile, ImageStat

ImageFile.LOAD_TRUNCATED_IMAGES = True

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_DIR


def is_valid_image(path: str) -> tuple[bool, str]:
    """Перевіряє чи зображення придатне для тренування."""
    try:
        img = Image.open(path)
        img.load()
        img = img.convert("RGB")

        # Занадто маленьке зображення
        if img.width < 50 or img.height < 50:
            return False, "замале"

        # Повністю чорне або біле зображення (зіпсоване)
        stat = ImageStat.Stat(img)
        mean_brightness = sum(stat.mean) / 3
        if mean_brightness < 5:
            return False, "повністю чорне"
        if mean_brightness > 250:
            return False, "повністю біле"

        return True, "ok"

    except Exception as e:
        return False, str(e)[:50]


def clean_folder(folder: str) -> tuple[int, int]:
    """Очищає одну папку. Повертає (всього, видалено)."""
    total   = 0
    removed = 0
    valid_ext = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

    for filename in os.listdir(folder):
        ext = os.path.splitext(filename)[1].lower()
        if ext not in valid_ext:
            continue

        total += 1
        path = os.path.join(folder, filename)
        ok, reason = is_valid_image(path)

        if not ok:
            os.remove(path)
            removed += 1

    return total, removed


def main():
    total_checked = 0
    total_removed = 0

    for split in ["train", "test"]:
        split_dir = os.path.join(BASE_DIR, "data", "car_data", split)
        if not os.path.exists(split_dir):
            continue

        print(f"\n=== {split.upper()} ===")
        classes = sorted(os.listdir(split_dir))

        for class_name in classes:
            class_dir = os.path.join(split_dir, class_name)
            if not os.path.isdir(class_dir):
                continue

            total, removed = clean_folder(class_dir)
            total_checked += total
            total_removed += removed

            if removed > 0:
                print(f"  {class_name}: видалено {removed}/{total}")

    print(f"\n{'='*50}")
    print(f"Перевірено: {total_checked} файлів")
    print(f"Видалено:   {total_removed} пошкоджених")
    print(f"Залишилось: {total_checked - total_removed} придатних")
    print(f"\nТепер запускай: python model/train.py")


if __name__ == "__main__":
    main()
