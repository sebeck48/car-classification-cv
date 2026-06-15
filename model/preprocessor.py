"""
preprocessor.py — підготовка зображення перед подачею в нейромережу.

Нейронна мережа не може отримати «сирий» PNG-файл.
Вона очікує тензор — числовий масив певного розміру та нормований.

Цей модуль перетворює будь-яке зображення у такий тензор.
"""

from PIL import Image
import torchvision.transforms as transforms
import torch

from config import MODEL_CONFIG


def build_transform() -> transforms.Compose:
    """
    Будує пайплайн трансформацій зображення.

    Кожен крок — це одна операція над зображенням:
      1. Resize      — зміна розміру до 224×224 пікселів
      2. CenterCrop  — обрізаємо центральну частину (позбуваємось країв)
      3. ToTensor    — конвертуємо PIL Image у тензор PyTorch (значення 0.0–1.0)
      4. Normalize   — нормалізація за mean/std ImageNet (так навчалась EfficientNet)

    Нормалізація ImageNet — стандарт для transfer learning:
      mean = [0.485, 0.456, 0.406]
      std  = [0.229, 0.224, 0.225]
    """
    image_size = MODEL_CONFIG["image_size"]

    return transforms.Compose([
        transforms.Resize((image_size + 32, image_size + 32)),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std= [0.229, 0.224, 0.225],
        ),
    ])


# Створюємо трансформацію один раз при імпорті модуля (не кожен виклик)
_transform = build_transform()


def preprocess_image(image_path: str) -> torch.Tensor:
    """
    Читає зображення з диска та повертає готовий тензор для моделі.

    Повертає тензор розміром [1, 3, 224, 224]:
      1 — batch size (один знімок)
      3 — три канали (R, G, B)
      224×224 — просторові розміри

    Args:
        image_path: абсолютний або відносний шлях до файлу зображення

    Raises:
        FileNotFoundError: якщо файл не знайдено
        OSError: якщо файл пошкоджено або не є зображенням
    """
    # Відкриваємо зображення через PIL
    image = Image.open(image_path)

    # Конвертуємо у RGB: деякі PNG мають 4 канали (RGBA) або є grayscale
    image = image.convert("RGB")

    # Застосовуємо пайплайн трансформацій
    tensor = _transform(image)

    # Додаємо розмірність батчу: [3, 224, 224] → [1, 3, 224, 224]
    tensor = tensor.unsqueeze(0)

    return tensor


def preprocess_pil_image(pil_image: Image.Image) -> torch.Tensor:
    """
    Те саме, але приймає вже відкритий PIL.Image.
    Корисно, коли зображення вже завантажене в GUI і не треба читати з диска.
    """
    image = pil_image.convert("RGB")
    tensor = _transform(image)
    return tensor.unsqueeze(0)
