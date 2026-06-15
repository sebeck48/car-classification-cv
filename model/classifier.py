"""
classifier.py — завантаження EfficientNet та інференс (розпізнавання).

Transfer Learning означає:
  1. Беремо EfficientNet вже навчену на ImageNet (1000 класів, мільйони фото)
  2. Замінюємо останній шар на свій (наша кількість класів авто)
  3. Донавчаємо на Stanford Cars Dataset

Цей файл завантажує таку навчену модель і виконує передбачення.
"""

import os
import torch
import torch.nn as nn
from torchvision import models
from PIL import Image

from config import MODEL_CONFIG
from model.preprocessor import preprocess_image, preprocess_pil_image


class CarClassifier:
    """
    Клас-обгортка над EfficientNet для розпізнавання марок авто.

    Використання:
        classifier = CarClassifier(class_labels=["Toyota Camry 2018", ...])
        classifier.load_weights("path/to/weights.pth")
        result = classifier.predict("photo.jpg")
    """

    def __init__(self, class_labels: list[str]):
        """
        Args:
            class_labels: список рядків — назви класів у тому порядку,
                          в якому вони були при тренуванні.
                          Наприклад: ["BMW 3 Series 2019", "Ford Mustang 2015", ...]
        """
        self.class_labels = class_labels
        self.num_classes = len(class_labels)

        # Визначаємо пристрій: GPU якщо є, інакше CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"[Model] Використовується пристрій: {self.device}")

        # Будуємо архітектуру моделі
        self.model = self._build_model()
        self.model.to(self.device)

        # Переводимо в режим оцінки (вимикає dropout, batch norm веде себе інакше)
        self.model.eval()

    # ── Побудова моделі ───────────────────────────────────────────────────────

    def _build_model(self) -> nn.Module:
        """
        Будує EfficientNet-B0 з заміненим класифікатором.

        EfficientNet-B0 архітектура:
          - features: згорткові блоки (витягують ознаки з фото)
          - avgpool:  глобальний пулінг (стискає карту ознак у вектор)
          - classifier: фінальні лінійні шари (наш custom шар)

        Ми замінюємо лише classifier[-1] щоб вихід = num_classes.
        """
        version = MODEL_CONFIG["efficientnet_version"]

        # Завантажуємо pretrained EfficientNet (ваги ImageNet)
        if version == "efficientnet_b0":
            model = models.efficientnet_b0(
                weights=models.EfficientNet_B0_Weights.IMAGENET1K_V1
            )
        elif version == "efficientnet_b2":
            model = models.efficientnet_b2(
                weights=models.EfficientNet_B2_Weights.IMAGENET1K_V1
            )
        else:
            raise ValueError(f"Непідтримувана версія: {version}")

        in_features = model.classifier[-1].in_features

        # Та сама архітектура що використовувалась при тренуванні в train.py
        model.classifier = nn.Sequential(
            nn.Dropout(p=0.4),
            nn.Linear(in_features, 512),
            nn.SiLU(),
            nn.Dropout(p=0.3),
            nn.Linear(512, self.num_classes),
        )

        return model

    # ── Завантаження ваг ──────────────────────────────────────────────────────

    def load_weights(self, weights_path: str = None) -> bool:
        """
        Завантажує навчені ваги з .pth файлу.

        Args:
            weights_path: шлях до файлу. Якщо None — береться з config.py

        Returns:
            True якщо успішно, False якщо файл не знайдено
        """
        if weights_path is None:
            weights_path = MODEL_CONFIG["weights_path"]

        if not os.path.exists(weights_path):
            print(f"[Model] Файл ваг не знайдено: {weights_path}")
            print("[Model] Модель працює з випадковими вагами (лише для тестів)")
            return False

        # map_location гарантує, що ваги завантажаться на правильний пристрій
        state_dict = torch.load(weights_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model.eval()
        print(f"[Model] Ваги завантажено: {weights_path}")
        return True

    # ── Інференс (передбачення) ───────────────────────────────────────────────

    @torch.no_grad()
    def predict(self, image_source) -> dict:
        """
        Розпізнає марку/модель авто на зображенні.
        Якщо tta_steps > 1 — застосовує Test Time Augmentation.

        Returns:
            {
                "label":       "Toyota Camry 2018",
                "confidence":  0.94,
                "top3": [...]
            }
        """
        if isinstance(image_source, str):
            pil_image = Image.open(image_source).convert("RGB")
        elif isinstance(image_source, Image.Image):
            pil_image = image_source.convert("RGB")
        else:
            raise TypeError("image_source має бути шляхом до файлу або PIL.Image")

        tta_steps = MODEL_CONFIG.get("tta_steps", 1)

        if tta_steps > 1:
            return self._predict_with_tta(pil_image, tta_steps)

        tensor = preprocess_pil_image(pil_image)

        # Переносимо тензор на той самий пристрій, що й модель
        tensor = tensor.to(self.device)

        # Пряме поширення (forward pass)
        logits = self.model(tensor)          # [1, num_classes] — «сирі» оцінки

        # Softmax: перетворює оцінки на ймовірності (сума = 1)
        probabilities = torch.softmax(logits, dim=1)[0]  # [num_classes]

        # Отримуємо топ-3 найбільш вірогідних класи
        top3_values, top3_indices = torch.topk(probabilities, k=min(3, self.num_classes))

        top3 = [
            {
                "label":      self.class_labels[idx.item()],
                "confidence": round(val.item(), 4),
            }
            for val, idx in zip(top3_values, top3_indices)
        ]

        best = top3[0]

        return {
            "label":      best["label"],
            "confidence": best["confidence"],
            "top3":       top3,
        }

    @torch.no_grad()
    def _predict_with_tta(self, pil_image: Image.Image, steps: int) -> dict:
        """
        Test Time Augmentation: робимо кілька передбачень з різними варіантами
        одного і того ж фото (повороти, відзеркалення, зміна яскравості),
        потім усереднюємо ймовірності. Результат стабільніший.
        """
        import torchvision.transforms as T

        tta_transforms = [
            # Оригінал
            T.Compose([
                T.Resize((MODEL_CONFIG["image_size"] + 32, MODEL_CONFIG["image_size"] + 32)),
                T.CenterCrop(MODEL_CONFIG["image_size"]),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]),
            # Горизонтальне відзеркалення
            T.Compose([
                T.Resize((MODEL_CONFIG["image_size"] + 32, MODEL_CONFIG["image_size"] + 32)),
                T.CenterCrop(MODEL_CONFIG["image_size"]),
                T.RandomHorizontalFlip(p=1.0),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]),
            # Обрізка зверху-зліва
            T.Compose([
                T.Resize((MODEL_CONFIG["image_size"] + 64, MODEL_CONFIG["image_size"] + 64)),
                T.CenterCrop(MODEL_CONFIG["image_size"]),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]),
            # Легкий поворот
            T.Compose([
                T.Resize((MODEL_CONFIG["image_size"] + 32, MODEL_CONFIG["image_size"] + 32)),
                T.RandomRotation(degrees=5),
                T.CenterCrop(MODEL_CONFIG["image_size"]),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]),
            # Яскравіше
            T.Compose([
                T.Resize((MODEL_CONFIG["image_size"] + 32, MODEL_CONFIG["image_size"] + 32)),
                T.CenterCrop(MODEL_CONFIG["image_size"]),
                T.ColorJitter(brightness=0.2),
                T.ToTensor(),
                T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
            ]),
        ]

        # Усереднюємо ймовірності по всіх аугментаціях
        avg_probs = torch.zeros(self.num_classes, device=self.device)

        for transform in tta_transforms[:steps]:
            tensor = transform(pil_image).unsqueeze(0).to(self.device)
            logits = self.model(tensor)
            probs  = torch.softmax(logits, dim=1)[0]
            avg_probs += probs

        avg_probs /= steps

        top3_values, top3_indices = torch.topk(avg_probs, k=min(3, self.num_classes))
        top3 = [
            {
                "label":      self.class_labels[idx.item()],
                "confidence": round(val.item(), 4),
            }
            for val, idx in zip(top3_values, top3_indices)
        ]

        return {
            "label":      top3[0]["label"],
            "confidence": top3[0]["confidence"],
            "top3":       top3,
        }

    def is_confident(self, confidence: float) -> bool:
        """Повертає True якщо впевненість вище порогу з config.py."""
        return confidence >= MODEL_CONFIG["confidence_threshold"]
