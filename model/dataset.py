"""
dataset.py — завантаження та підготовка датасету для тренування.

PyTorch очікує клас Dataset що вміє:
  - __len__()     → скільки всього зображень
  - __getitem__(i) → повернути i-те зображення + мітку класу
"""

import os
from PIL import Image, ImageFile
from torch.utils.data import Dataset
import torchvision.transforms as transforms

# Дозволяє PIL завантажувати пошкоджені/обрізані файли замість краша
ImageFile.LOAD_TRUNCATED_IMAGES = True


def build_train_transform(image_size: int = 224) -> transforms.Compose:
    """
    Трансформації для ТРЕНУВАННЯ — включають аугментацію.

    Аугментація = штучне збільшення датасету через випадкові зміни фото.
    Це допомагає моделі не «зазубрювати» тренувальні фото.
    """
    return transforms.Compose([
        # Випадкове обрізання (модель не прив'язується до центру)
        transforms.RandomResizedCrop(image_size, scale=(0.7, 1.0)),

        # Випадкове горизонтальне відзеркалення
        transforms.RandomHorizontalFlip(),

        # Невелика зміна яскравості, контрасту, насиченості
        transforms.ColorJitter(
            brightness=0.3,
            contrast=0.3,
            saturation=0.2,
        ),

        # Невеликий випадковий поворот (авто рідко їздять під кутом 30°)
        transforms.RandomRotation(degrees=10),

        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std= [0.229, 0.224, 0.225],
        ),
    ])


def build_val_transform(image_size: int = 224) -> transforms.Compose:
    """
    Трансформації для ВАЛІДАЦІЇ — без аугментації, лише нормалізація.
    При оцінці точності не потрібна випадковість.
    """
    return transforms.Compose([
        transforms.Resize((image_size + 32, image_size + 32)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std= [0.229, 0.224, 0.225],
        ),
    ])


class CarsDataset(Dataset):
    """
    Датасет Stanford Cars.

    Очікує таку структуру папок:
        root_dir/
            Клас 1/
                фото1.jpg
                фото2.jpg
            Клас 2/
                фото3.jpg
            ...

    Де назва папки = назва класу (марка + модель + рік).
    """

    def __init__(self, root_dir: str, transform=None):
        """
        Args:
            root_dir:  шлях до папки train/ або test/
            transform: пайплайн трансформацій
        """
        self.root_dir  = root_dir
        self.transform = transform

        # Список класів = список підпапок, відсортований за алфавітом
        self.classes = sorted([
            d for d in os.listdir(root_dir)
            if os.path.isdir(os.path.join(root_dir, d))
        ])

        # Словник: назва класу → числовий індекс
        self.class_to_idx = {cls: i for i, cls in enumerate(self.classes)}

        # Список пар (шлях_до_фото, індекс_класу)
        self.samples = self._load_samples()

        print(f"[Dataset] Завантажено: {len(self.samples)} фото, {len(self.classes)} класів")
        print(f"[Dataset] Перші 3 класи: {self.classes[:3]}")

    def _load_samples(self) -> list[tuple[str, int]]:
        """Збирає всі пари (шлях, клас) з папок."""
        samples = []
        valid_ext = {".jpg", ".jpeg", ".png", ".bmp"}

        for class_name in self.classes:
            class_dir = os.path.join(self.root_dir, class_name)
            class_idx = self.class_to_idx[class_name]

            for filename in os.listdir(class_dir):
                ext = os.path.splitext(filename)[1].lower()
                if ext in valid_ext:
                    path = os.path.join(class_dir, filename)
                    samples.append((path, class_idx))

        return samples

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple:
        """Повертає (тензор_зображення, індекс_класу) для i-го елементу."""
        img_path, label = self.samples[idx]

        # Деякі завантажені фото можуть бути пошкодженими — пропускаємо їх
        try:
            image = Image.open(img_path).convert("RGB")
        except Exception:
            # Повертаємо чорне зображення замість краша
            image = Image.new("RGB", (224, 224), color=0)

        if self.transform:
            image = self.transform(image)

        return image, label
