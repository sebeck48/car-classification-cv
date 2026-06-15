"""
merge_test_to_train.py — копіює фото з test/ у train/ для збільшення датасету.

Після цього у train/ буде вдвічі більше якісних оригінальних фото.

Запуск:
    python tools/merge_test_to_train.py
"""

import os
import sys
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import BASE_DIR

TRAIN_DIR = os.path.join(BASE_DIR, "data", "car_data", "train")
TEST_DIR  = os.path.join(BASE_DIR, "data", "car_data", "test")


def main():
    classes = sorted(os.listdir(TEST_DIR))
    total_copied = 0

    for class_name in classes:
        test_class_dir  = os.path.join(TEST_DIR,  class_name)
        train_class_dir = os.path.join(TRAIN_DIR, class_name)

        if not os.path.isdir(test_class_dir):
            continue

        os.makedirs(train_class_dir, exist_ok=True)

        # Копіюємо кожне фото з test/ у train/ з новою назвою
        copied = 0
        for filename in os.listdir(test_class_dir):
            ext = os.path.splitext(filename)[1].lower()
            if ext not in {".jpg", ".jpeg", ".png"}:
                continue

            src = os.path.join(test_class_dir, filename)
            dst = os.path.join(train_class_dir, f"test_{filename}")

            if not os.path.exists(dst):
                shutil.copy2(src, dst)
                copied += 1

        total_copied += copied
        print(f"  {class_name}: +{copied} фото")

    print(f"\nВсього скопійовано: {total_copied} фото")
    print(f"Тепер очисти і перетренуй:")
    print(f"  python tools/clean_dataset.py")
    print(f"  python model/train.py")


if __name__ == "__main__":
    main()
