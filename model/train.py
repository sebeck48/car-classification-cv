"""
train.py — покращений скрипт тренування.

Техніки що застосовуються:
  1. EfficientNet-B2 — точніша архітектура ніж B0
  2. Градуальне розморожування — шари відкриваються поступово
  3. Label Smoothing — модель не стає надто впевненою (краща узагальнюваність)
  4. Cosine Annealing LR — плавне зменшення learning rate
  5. Mixed Precision (AMP) — вдвічі швидше на GPU з мінімальною втратою точності
  6. Early Stopping — зупиняємо якщо модель перестала покращуватись

Запуск:
    python model/train.py
"""

import os
import sys
import time

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import models

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from model.dataset import CarsDataset, build_train_transform, build_val_transform
from config import BASE_DIR


TRAIN_CONFIG = {
    "data_dir":    os.path.join(BASE_DIR, "data", "car_data"),
    "weights_dir": os.path.join(BASE_DIR, "model", "weights"),

    # ── Архітектура ───────────────────────────────────────────────────────────
    "efficientnet_version": "efficientnet_b2",
    "image_size":           260,       # B2 → 260, B0 → 224, B3 → 300

    # ── Параметри тренування ──────────────────────────────────────────────────
    "batch_size":           16,
    "num_epochs":           50,
    "num_workers":          2,

    # ── Learning rate ─────────────────────────────────────────────────────────
    "lr_head":              1e-4,    # для нового класифікатора
    "lr_finetune":          1e-5,    # для всієї мережі (fine-tuning)

    # ── Градуальне розморожування ─────────────────────────────────────────────
    # Список (епоха, кількість_блоків_що_відкриваємо)
    # EfficientNet-B2 має 7 блоків (features[0]..features[7] + features[8])
    "unfreeze_schedule": [
        (1,  0),   # епохи 1–4:  лише classifier
        (5,  3),   # епохи 5–9:  + останні 3 блоки
        (10, 6),   # епохи 10–14: + ще 3 блоки
        (15, 9),   # епохи 15+:  всі шари
    ],

    # ── Зупинка ───────────────────────────────────────────────────────────────
    "early_stopping_patience": 7,    # зупиняємо якщо 7 епох без покращення

    # ── Label Smoothing ───────────────────────────────────────────────────────
    # 0.1 = 10% впевненості «розмазується» між іншими класами
    "label_smoothing": 0.1,

    # ── Mixed Precision (тільки GPU) ──────────────────────────────────────────
    "use_amp": False,   # вимкнено — запобігає NaN на деяких зображеннях
}


# ── Побудова моделі ───────────────────────────────────────────────────────────

def build_model(num_classes: int) -> nn.Module:
    version = TRAIN_CONFIG["efficientnet_version"]

    weights_map = {
        "efficientnet_b0": models.EfficientNet_B0_Weights.IMAGENET1K_V1,
        "efficientnet_b2": models.EfficientNet_B2_Weights.IMAGENET1K_V1,
        "efficientnet_b3": models.EfficientNet_B3_Weights.IMAGENET1K_V1,
    }
    model_map = {
        "efficientnet_b0": models.efficientnet_b0,
        "efficientnet_b2": models.efficientnet_b2,
        "efficientnet_b3": models.efficientnet_b3,
    }

    model = model_map[version](weights=weights_map[version])

    # Заморожуємо всі шари на старті
    for param in model.parameters():
        param.requires_grad = False

    # Замінюємо класифікатор (він одразу trainable)
    in_features = model.classifier[-1].in_features
    model.classifier = nn.Sequential(
        nn.Dropout(p=0.4),
        nn.Linear(in_features, 512),
        nn.SiLU(),               # SiLU = swish, краще ніж ReLU для EfficientNet
        nn.Dropout(p=0.3),
        nn.Linear(512, num_classes),
    )
    return model


def apply_unfreeze_schedule(model: nn.Module, epoch: int):
    """
    Поступово відкриває шари моделі згідно з розкладом.

    Ідея: спочатку навчаємо лише новий класифікатор,
    потім поступово «підтягуємо» все більше шарів знизу вгору.
    Так стара інформація ImageNet не знищується одразу.
    """
    schedule = TRAIN_CONFIG["unfreeze_schedule"]

    blocks_to_unfreeze = 0
    for (start_epoch, blocks) in schedule:
        if epoch >= start_epoch:
            blocks_to_unfreeze = blocks

    # features — це список блоків EfficientNet: [0, 1, 2, ..., 8]
    total_blocks = len(list(model.features.children()))
    freeze_until = total_blocks - blocks_to_unfreeze

    for i, block in enumerate(model.features.children()):
        trainable = (i >= freeze_until)
        for param in block.parameters():
            param.requires_grad = trainable

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params     = sum(p.numel() for p in model.parameters())
    print(f"  Trainable параметрів: {trainable_params:,} / {total_params:,} "
          f"({100 * trainable_params / total_params:.1f}%)")


# ── Одна епоха ────────────────────────────────────────────────────────────────

def run_epoch(model, loader, criterion, optimizer, device, scaler, is_training: bool):
    model.train(is_training)

    total_loss    = 0.0
    correct       = 0
    total_samples = 0
    use_amp       = TRAIN_CONFIG["use_amp"] and device.type == "cuda"

    for batch_idx, (images, labels) in enumerate(loader):
        images = images.to(device)
        labels = labels.to(device)

        if is_training:
            optimizer.zero_grad()

        # Mixed Precision: обчислення у float16 замість float32 → вдвічі швидше
        with torch.autocast(device_type=device.type, enabled=use_amp):
            outputs = model(images)
            loss    = criterion(outputs, labels)

        if is_training:
            if use_amp:
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                # Gradient clipping — запобігає «вибуху» градієнтів
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
            else:
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()

        total_loss    += loss.item() * images.size(0)
        predicted      = outputs.argmax(dim=1)
        correct       += (predicted == labels).sum().item()
        total_samples += images.size(0)

        if batch_idx % 20 == 0:
            print(f"  Батч {batch_idx}/{len(loader)} | loss: {loss.item():.4f}", end="\r")

    return total_loss / total_samples, 100.0 * correct / total_samples


# ── Early Stopping ────────────────────────────────────────────────────────────

class EarlyStopping:
    """Зупиняє тренування якщо модель не покращується N епох поспіль."""

    def __init__(self, patience: int):
        self.patience   = patience
        self.best_acc   = 0.0
        self.counter    = 0
        self.should_stop = False

    def step(self, val_acc: float) -> bool:
        if val_acc > self.best_acc:
            self.best_acc = val_acc
            self.counter  = 0
        else:
            self.counter += 1
            print(f"  Early stopping: {self.counter}/{self.patience}")
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop


# ── Головна функція ───────────────────────────────────────────────────────────

def train():
    cfg    = TRAIN_CONFIG
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[Train] Пристрій: {device}")
    if device.type == "cuda":
        print(f"[Train] GPU: {torch.cuda.get_device_name(0)}")

    # ── Датасет ───────────────────────────────────────────────────────────────
    train_dir = os.path.join(cfg["data_dir"], "train")
    val_dir   = os.path.join(cfg["data_dir"], "test")

    if not os.path.exists(train_dir):
        print(f"ПОМИЛКА: папка не знайдена: {train_dir}")
        return

    train_dataset = CarsDataset(train_dir, build_train_transform(cfg["image_size"]))
    val_dataset   = CarsDataset(val_dir,   build_val_transform(cfg["image_size"]))

    train_loader = DataLoader(
        train_dataset, batch_size=cfg["batch_size"],
        shuffle=True,  num_workers=cfg["num_workers"], pin_memory=True,
    )
    val_loader = DataLoader(
        val_dataset,   batch_size=cfg["batch_size"],
        shuffle=False, num_workers=cfg["num_workers"], pin_memory=True,
    )

    num_classes = len(train_dataset.classes)
    print(f"[Train] Класів: {num_classes} | Train: {len(train_dataset)} | Val: {len(val_dataset)}")

    # ── Модель, функція втрат, оптимізатор ───────────────────────────────────
    model     = build_model(num_classes).to(device)
    criterion = nn.CrossEntropyLoss(label_smoothing=cfg["label_smoothing"])
    optimizer = torch.optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=cfg["lr_head"], weight_decay=1e-4,
    )

    # Cosine Annealing: lr зменшується за кривою косинуса → плавне навчання
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=cfg["num_epochs"], eta_min=1e-6
    )

    # Scaler для mixed precision (на CPU нічого не робить)
    scaler = torch.cuda.amp.GradScaler(enabled=(cfg["use_amp"] and device.type == "cuda"))

    early_stopping = EarlyStopping(patience=cfg["early_stopping_patience"])

    os.makedirs(cfg["weights_dir"], exist_ok=True)
    best_weights_path = os.path.join(cfg["weights_dir"], "efficientnet_cars.pth")
    best_accuracy = 0.0

    # ── Цикл епох ─────────────────────────────────────────────────────────────
    for epoch in range(1, cfg["num_epochs"] + 1):
        print(f"\n── Епоха {epoch}/{cfg['num_epochs']} ──────────────────────────────")

        # Оновлюємо які шари навчаються
        apply_unfreeze_schedule(model, epoch)

        # На епосі 10 знижуємо lr для fine-tuning
        if epoch == 10:
            for g in optimizer.param_groups:
                g["lr"] = cfg["lr_finetune"]
            print(f"  LR знижено до {cfg['lr_finetune']}")

        start = time.time()
        train_loss, train_acc = run_epoch(
            model, train_loader, criterion, optimizer, device, scaler, is_training=True
        )
        with torch.no_grad():
            val_loss, val_acc = run_epoch(
                model, val_loader, criterion, optimizer, device, scaler, is_training=False
            )

        scheduler.step()

        print(f"\n  Train  loss={train_loss:.4f}  acc={train_acc:.1f}%")
        print(f"  Val    loss={val_loss:.4f}  acc={val_acc:.1f}%")
        print(f"  LR={optimizer.param_groups[0]['lr']:.2e} | Час={time.time()-start:.0f}с")

        if val_acc > best_accuracy:
            best_accuracy = val_acc
            torch.save(model.state_dict(), best_weights_path)
            print(f"  ✓ Збережено найкращу модель: {val_acc:.1f}%")

        if early_stopping.step(val_acc):
            print(f"\n[Train] Early stopping після епохи {epoch}")
            break

    print(f"\n[Train] Готово! Найкраща точність: {best_accuracy:.1f}%")

    labels_path = os.path.join(cfg["weights_dir"], "class_labels.txt")
    with open(labels_path, "w", encoding="utf-8") as f:
        f.write("\n".join(train_dataset.classes))
    print(f"[Train] Мітки збережено: {labels_path}")


if __name__ == "__main__":
    train()
