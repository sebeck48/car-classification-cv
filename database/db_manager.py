"""
db_manager.py — менеджер підключення до PostgreSQL.

Цей модуль відповідає лише за одне:
  - відкрити з'єднання з базою даних
  - виконати запит
  - повернути результат
  - закрити з'єднання

Всю логіку (що шукати, що виводити) залишаємо в інших модулях.
"""

import psycopg2
import psycopg2.extras   # для отримання результатів у вигляді словників
from config import DB_CONFIG


class DatabaseManager:
    """Клас для роботи з PostgreSQL базою даних."""

    def __init__(self):
        # З'єднання буде встановлюватись лише коли потрібно (lazy connection)
        self._connection = None

    # ── Підключення та відключення ────────────────────────────────────────────

    def connect(self):
        """Відкриває з'єднання з базою даних."""
        try:
            self._connection = psycopg2.connect(**DB_CONFIG)
            print("[DB] З'єднання встановлено успішно.")
        except psycopg2.OperationalError as e:
            print(f"[DB] Помилка підключення: {e}")
            self._connection = None

    def disconnect(self):
        """Закриває з'єднання, якщо воно відкрите."""
        if self._connection:
            self._connection.close()
            self._connection = None
            print("[DB] З'єднання закрито.")

    def is_connected(self) -> bool:
        """Перевіряє, чи активне з'єднання."""
        return self._connection is not None and self._connection.closed == 0

    # ── Основний метод виконання запитів ──────────────────────────────────────

    def _execute_query(self, query: str, params: tuple = None) -> list[dict]:
        """
        Внутрішній метод. Виконує SQL-запит і повертає список рядків
        у вигляді словників {назва_колонки: значення}.

        params — кортеж значень для підстановки замість %s у запиті
                 (захист від SQL-ін'єкцій).
        """
        if not self.is_connected():
            self.connect()

        if not self.is_connected():
            return []   # не вдалось підключитись — повертаємо порожній список

        try:
            # RealDictCursor повертає рядки як словники Python
            with self._connection.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cursor:
                cursor.execute(query, params)
                results = cursor.fetchall()
                # Конвертуємо RealDictRow у звичайні dict для зручності
                return [dict(row) for row in results]

        except psycopg2.Error as e:
            print(f"[DB] Помилка запиту: {e}")
            self._connection.rollback()   # скасовуємо незавершену транзакцію
            return []

    # ── Публічні методи пошуку ────────────────────────────────────────────────

    def get_car_by_label(self, class_label: str) -> dict | None:
        """
        Шукає інформацію про авто за міткою класу, яку повернула нейромережа.

        Повертає словник з усіма полями або None, якщо не знайдено.

        Приклад:
            result = db.get_car_by_label("Toyota Camry 2018")
        """
        query = """
            SELECT
                b.name          AS brand,
                m.model_name,
                m.generation,
                m.year_start,
                m.year_end,
                m.body_type,
                m.engine_volume,
                m.horsepower,
                m.description,
                m.engines,
                m.trims,
                b.country       AS brand_country
            FROM car_models m
            JOIN brands b ON b.id = m.brand_id
            WHERE m.class_label = %s
            LIMIT 1
        """
        results = self._execute_query(query, (class_label,))
        return results[0] if results else None

    def get_all_class_labels(self) -> list[str]:
        """
        Повертає список усіх міток класів з бази.
        Використовується при ініціалізації моделі, щоб перевірити
        що мітки в БД і мітки моделі збігаються.
        """
        query = "SELECT class_label FROM car_models ORDER BY class_label"
        results = self._execute_query(query)
        return [row["class_label"] for row in results]

    def search_cars(self, brand: str = None, model: str = None) -> list[dict]:
        """
        Пошук автомобілів за маркою та/або моделлю (для майбутнього функціоналу).
        Підтримує часткове співпадіння (ILIKE).
        """
        conditions = []
        params = []

        if brand:
            conditions.append("b.name ILIKE %s")
            params.append(f"%{brand}%")

        if model:
            conditions.append("m.model_name ILIKE %s")
            params.append(f"%{model}%")

        where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""

        query = f"""
            SELECT
                b.name AS brand,
                m.model_name,
                m.year_start,
                m.year_end,
                m.body_type,
                m.class_label
            FROM car_models m
            JOIN brands b ON b.id = m.brand_id
            {where_clause}
            ORDER BY b.name, m.model_name
        """
        return self._execute_query(query, tuple(params))

    # ── Контекстний менеджер (with DatabaseManager() as db:) ─────────────────

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
