"""
app.py — головне вікно програми (Tkinter GUI).

Структура вікна:
┌─────────────────────────────────────────────┐
│  [Заголовок]                                │
├─────────────────┬───────────────────────────┤
│                 │  Марка: Toyota             │
│   [Прев'ю       │  Модель: Camry             │
│    зображення]  │  Рік: 2017–2024            │
│                 │  Тип: Sedan                │
│                 │  Двигун: 2.5 л / 203 к.с. │
│                 │                            │
│                 │  Впевненість: 94%          │
├─────────────────┴───────────────────────────┤
│  [Завантажити фото]        [Очистити]        │
└─────────────────────────────────────────────┘
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

from config import GUI_CONFIG, ALLOWED_IMAGE_EXTENSIONS
from database.db_manager import DatabaseManager
from model.classifier import CarClassifier


class CarRecognitionApp:
    """Головний клас застосунку."""

    def __init__(self, root: tk.Tk, classifier: CarClassifier, db: DatabaseManager):
        """
        Args:
            root:       кореневий Tk об'єкт
            classifier: ініціалізована модель розпізнавання
            db:         менеджер бази даних
        """
        self.root = root
        self.classifier = classifier
        self.db = db

        # Поточне завантажене зображення (PIL.Image)
        self._current_image: Image.Image | None = None

        self._configure_root()
        self._build_ui()

    # ── Налаштування вікна ────────────────────────────────────────────────────

    def _configure_root(self):
        """Загальні параметри головного вікна."""
        cfg = GUI_CONFIG
        self.root.title(cfg["window_title"])
        self.root.geometry(f"{cfg['window_width']}x{cfg['window_height']}")
        self.root.resizable(False, False)
        self.root.configure(bg=cfg["bg_color"])

        # Стилі ttk (для кнопок та міток)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "Accent.TButton",
            background=cfg["accent_color"],
            foreground="#1e1e2e",
            font=("Helvetica", 11, "bold"),
            padding=8,
        )
        style.configure(
            "TLabel",
            background=cfg["bg_color"],
            foreground=cfg["text_color"],
            font=("Helvetica", 11),
        )

    # ── Побудова UI ───────────────────────────────────────────────────────────

    def _build_ui(self):
        """Будує всі елементи інтерфейсу."""
        cfg = GUI_CONFIG

        # ── Заголовок ─────────────────────────────────────────────────────────
        header = tk.Label(
            self.root,
            text="Розпізнавання автомобілів",
            bg=cfg["bg_color"],
            fg=cfg["accent_color"],
            font=("Helvetica", 16, "bold"),
            pady=12,
        )
        header.pack(fill="x")

        # ── Основна область (два стовпці) ─────────────────────────────────────
        main_frame = tk.Frame(self.root, bg=cfg["bg_color"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Лівий стовпець — прев'ю зображення
        self._build_image_panel(main_frame)

        # Правий стовпець — результати
        self._build_result_panel(main_frame)

        # ── Кнопки внизу ─────────────────────────────────────────────────────
        self._build_buttons()

    def _build_image_panel(self, parent):
        """Панель прев'ю завантаженого фото."""
        cfg = GUI_CONFIG
        max_w = cfg["preview_max_width"]
        max_h = cfg["preview_max_height"]

        # Фрейм з фіксованим розміром у пікселях
        frame = tk.Frame(
            parent,
            bg="#2a2a3e",
            bd=1,
            relief="solid",
            width=max_w,
            height=max_h,
        )
        frame.pack(side="left", padx=(0, 10))
        frame.pack_propagate(False)   # не дозволяємо дочірнім елементам змінювати розмір

        self.image_label = tk.Label(
            frame,
            text="Фото ще не\nзавантажено\n\nНатисніть\n«Завантажити фото»",
            bg="#2a2a3e",
            fg="#6c7086",
            font=("Helvetica", 12),
        )
        self.image_label.pack(expand=True, fill="both")

    def _build_result_panel(self, parent):
        """Панель з результатами розпізнавання."""
        cfg = GUI_CONFIG

        frame = tk.Frame(parent, bg=cfg["bg_color"])
        frame.pack(side="right", fill="both", padx=(10, 0))

        tk.Label(
            frame,
            text="Результат",
            bg=cfg["bg_color"],
            fg=cfg["accent_color"],
            font=("Helvetica", 13, "bold"),
        ).pack(anchor="w", pady=(8, 12))

        # Динамічні поля результату
        fields = [
            ("brand",   "Марка:"),
            ("model",   "Модель:"),
            ("years",   "Роки випуску:"),
            ("body",    "Тип кузова:"),
            ("engines", "Двигуни:"),
            ("trims",   "Комплектації:"),
            ("country", "Країна:"),
        ]

        self._result_vars: dict[str, tk.StringVar] = {}

        for key, label_text in fields:
            row = tk.Frame(frame, bg=cfg["bg_color"])
            row.pack(fill="x", pady=3)

            tk.Label(
                row,
                text=label_text,
                bg=cfg["bg_color"],
                fg="#6c7086",
                font=("Helvetica", 10),
                width=16,
                anchor="w",
            ).pack(side="left")

            var = tk.StringVar(value="—")
            self._result_vars[key] = var

            tk.Label(
                row,
                textvariable=var,
                bg=cfg["bg_color"],
                fg=cfg["text_color"],
                font=("Helvetica", 10, "bold"),
                anchor="w",
            ).pack(side="left")

        # Роздільник
        tk.Frame(frame, bg="#45475a", height=1).pack(fill="x", pady=12)

        # Впевненість моделі
        confidence_row = tk.Frame(frame, bg=cfg["bg_color"])
        confidence_row.pack(fill="x", pady=3)

        tk.Label(
            confidence_row,
            text="Впевненість:",
            bg=cfg["bg_color"],
            fg="#6c7086",
            font=("Helvetica", 10),
            width=16,
            anchor="w",
        ).pack(side="left")

        self._confidence_var = tk.StringVar(value="—")
        self._confidence_label = tk.Label(
            confidence_row,
            textvariable=self._confidence_var,
            bg=cfg["bg_color"],
            fg=cfg["text_color"],
            font=("Helvetica", 11, "bold"),
            anchor="w",
        )
        self._confidence_label.pack(side="left")

        # Опис авто
        tk.Frame(frame, bg="#45475a", height=1).pack(fill="x", pady=12)

        self._description_text = tk.Text(
            frame,
            bg="#2a2a3e",
            fg=cfg["text_color"],
            font=("Helvetica", 9),
            height=5,
            wrap="word",
            state="disabled",
            relief="flat",
        )
        self._description_text.pack(fill="x")

    def _build_buttons(self):
        """Панель кнопок унизу вікна."""
        cfg = GUI_CONFIG

        btn_frame = tk.Frame(self.root, bg=cfg["bg_color"])
        btn_frame.pack(fill="x", padx=20, pady=10)

        # Кнопка завантаження
        load_btn = tk.Button(
            btn_frame,
            text="Завантажити фото",
            command=self._on_load_image,
            bg=cfg["accent_color"],
            fg="#1e1e2e",
            font=("Helvetica", 11, "bold"),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
        )
        load_btn.pack(side="left", padx=(0, 10))

        # Кнопка очищення
        clear_btn = tk.Button(
            btn_frame,
            text="Очистити",
            command=self._on_clear,
            bg="#45475a",
            fg=cfg["text_color"],
            font=("Helvetica", 11),
            relief="flat",
            padx=20,
            pady=8,
            cursor="hand2",
        )
        clear_btn.pack(side="left")

        # Статусний рядок
        self._status_var = tk.StringVar(value="Готовий до роботи")
        tk.Label(
            btn_frame,
            textvariable=self._status_var,
            bg=cfg["bg_color"],
            fg="#6c7086",
            font=("Helvetica", 9),
        ).pack(side="right")

    # ── Обробники подій ───────────────────────────────────────────────────────

    def _on_load_image(self):
        """Відкриває діалог вибору файлу та запускає розпізнавання."""
        # Формуємо рядок фільтру для файлового діалогу
        ext_filter = " ".join(f"*{e}" for e in ALLOWED_IMAGE_EXTENSIONS)
        file_path = filedialog.askopenfilename(
            title="Виберіть фото автомобіля",
            filetypes=[
                ("Зображення", ext_filter),
                ("Всі файли", "*.*"),
            ],
        )

        if not file_path:
            return   # користувач натиснув «Скасувати»

        self._status_var.set("Обробка зображення...")
        self.root.update()   # перемальовуємо вікно щоб показати статус

        try:
            self._current_image = Image.open(file_path)
            self._show_preview(self._current_image)
            self._run_recognition(self._current_image)
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося завантажити зображення:\n{e}")
            self._status_var.set("Помилка завантаження")

    def _run_recognition(self, image: Image.Image):
        """Запускає модель і виводить результат на екран."""
        self._status_var.set("Розпізнавання...")
        self.root.update()

        try:
            # Крок 1: отримуємо передбачення від моделі
            prediction = self.classifier.predict(image)
            label      = prediction["label"]
            confidence = prediction["confidence"]

            # Крок 2: запит до бази даних
            car_info = self.db.get_car_by_label(label)

            # Крок 3: оновлюємо UI
            self._update_results(label, confidence, car_info)

            status = f"Розпізнано: {label} ({confidence:.0%})"
            self._status_var.set(status)

        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка розпізнавання:\n{e}")
            self._status_var.set("Помилка розпізнавання")

    def _on_clear(self):
        """Скидає все до початкового стану."""
        self._current_image = None

        # Повертаємо placeholder
        self.image_label.configure(
            image="",
            text="Фото ще не завантажено\n\nНатисніть «Завантажити фото»",
        )

        # Скидаємо поля результату
        for var in self._result_vars.values():
            var.set("—")
        self._confidence_var.set("—")
        self._confidence_label.configure(fg=GUI_CONFIG["text_color"])
        self._set_description("")
        self._status_var.set("Готовий до роботи")

    # ── Допоміжні методи ─────────────────────────────────────────────────────

    def _show_preview(self, image: Image.Image):
        """Масштабує та відображає зображення у панелі прев'ю."""
        cfg = GUI_CONFIG
        max_w = cfg["preview_max_width"]
        max_h = cfg["preview_max_height"]

        # Пропорційне масштабування
        img_copy = image.copy()
        img_copy.thumbnail((max_w, max_h), Image.LANCZOS)

        # Конвертуємо у Tkinter-сумісний формат
        photo = ImageTk.PhotoImage(img_copy)

        # Оновлюємо Label (зберігаємо посилання на photo, бо Python може прибрати його з пам'яті)
        self.image_label.configure(image=photo, text="")
        self.image_label._photo_ref = photo   # запобігаємо garbage collection

    def _update_results(self, label: str, confidence: float, car_info: dict | None):
        """Заповнює поля результату даними з БД або fallback-значеннями."""
        cfg = GUI_CONFIG

        if car_info:
            year_end = car_info.get("year_end") or "н.ч."

            self._result_vars["brand"].set(car_info.get("brand", "—"))
            self._result_vars["model"].set(car_info.get("model_name", "—"))
            self._result_vars["years"].set(
                f"{car_info.get('year_start', '?')} – {year_end}"
            )
            self._result_vars["body"].set(car_info.get("body_type", "—").capitalize())
            self._result_vars["engines"].set(car_info.get("engines") or "—")
            self._result_vars["trims"].set(car_info.get("trims") or "—")
            self._result_vars["country"].set(car_info.get("brand_country", "—"))
            self._set_description(car_info.get("description") or "")
        else:
            self._result_vars["brand"].set(label)
            self._result_vars["model"].set("(дані відсутні в БД)")
            for key in ["years", "body", "engines", "trims", "country"]:
                self._result_vars[key].set("—")
            self._set_description("")

        # Колір впевненості: зелений/жовтий
        conf_text = f"{confidence:.1%}"
        if self.classifier.is_confident(confidence):
            color = cfg["success_color"]
        else:
            color = cfg["warning_color"]
            conf_text += "  ⚠ Низька впевненість"

        self._confidence_var.set(conf_text)
        self._confidence_label.configure(fg=color)

    def _set_description(self, text: str):
        """Оновлює текст у полі опису (Text-віджет потребує спеціального підходу)."""
        self._description_text.configure(state="normal")
        self._description_text.delete("1.0", "end")
        if text:
            self._description_text.insert("1.0", text)
        self._description_text.configure(state="disabled")
