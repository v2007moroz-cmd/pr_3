"""Паттерни Singleton та Factory Method."""

from abc import ABC, abstractmethod
from datetime import datetime
import json


class SingletonMeta(type):
    """Метаклас для реалізації патерну Singleton."""

    _instances: dict[type, object] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class LogFormatter(ABC):
    """Абстрактний базовий клас форматера логів."""

    @abstractmethod
    def format(self, level: str, message: str, timestamp: datetime) -> str:
        """Форматувати повідомлення логу."""
        raise NotImplementedError


class PlainFormatter(LogFormatter):
    """Простий текстовий формат."""

    def format(self, level: str, message: str, timestamp: datetime) -> str:
        return f"[{level}] {timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {message}"


class JSONFormatter(LogFormatter):
    """JSON-формат логування."""

    def format(self, level: str, message: str, timestamp: datetime) -> str:
        return json.dumps(
            {
                "level": level,
                "time": timestamp.isoformat(timespec="seconds"),
                "message": message,
            },
            ensure_ascii=False,
        )


class ColorFormatter(LogFormatter):
    """Кольоровий формат для терміналу."""

    COLORS = {
        "DEBUG": "\033[90m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
    }
    RESET = "\033[0m"

    def format(self, level: str, message: str, timestamp: datetime) -> str:
        color = self.COLORS.get(level, "")
        text = f"[{level}] {timestamp.strftime('%H:%M:%S')} - {message}"
        return f"{color}{text}{self.RESET}"


class FormatterFactory:
    """Фабрика форматерів із підтримкою реєстрації нових типів."""

    _formatters: dict[str, type[LogFormatter]] = {
        "plain": PlainFormatter,
        "json": JSONFormatter,
        "color": ColorFormatter,
    }

    @classmethod
    def register(cls, name: str, formatter_cls: type[LogFormatter]):
        """Зареєструвати новий тип форматера."""
        if not issubclass(formatter_cls, LogFormatter):
            raise TypeError("formatter_cls повинен наслідувати LogFormatter")
        cls._formatters[name] = formatter_cls

    @classmethod
    def create(cls, name: str) -> LogFormatter:
        """Створити форматер за іменем."""
        if name not in cls._formatters:
            raise ValueError(f"Невідомий форматер: {name}")
        return cls._formatters[name]()

    @classmethod
    def available(cls) -> list[str]:
        """Повернути список доступних форматерів."""
        return list(cls._formatters.keys())


class Logger(metaclass=SingletonMeta):
    """Логер із підтримкою рівнів та змінних форматерів."""

    LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}

    def __init__(self, formatter_name: str = "plain", min_level: str = "DEBUG"):
        if not hasattr(self, "_initialized"):
            self._formatter = FormatterFactory.create(formatter_name)
            self._min_level = min_level
            self._log_history: list[str] = []
            self._initialized = True

    def set_formatter(self, name: str):
        self._formatter = FormatterFactory.create(name)

    def log(self, level: str, message: str):
        if level not in self.LEVELS:
            raise ValueError(f"Невідомий рівень логування: {level}")

        if self.LEVELS[level] < self.LEVELS[self._min_level]:
            return

        formatted = self._formatter.format(level, message, datetime.now())
        print(formatted)
        self._log_history.append(formatted)

    def debug(self, msg: str):
        self.log("DEBUG", msg)

    def info(self, msg: str):
        self.log("INFO", msg)

    def warning(self, msg: str):
        self.log("WARNING", msg)

    def error(self, msg: str):
        self.log("ERROR", msg)

    def get_history(self) -> list[str]:
        return self._log_history[:]


def main():
    logger1 = Logger("plain", "DEBUG")
    logger2 = Logger("json", "INFO")
    print(f"Singleton: {logger1 is logger2}")

    logger1.info("Система запущена")
    logger1.warning("Мало пам'яті")
    logger1.error("Помилка з'єднання")

    print("\nЗміна форматера на JSON:")
    logger1.set_formatter("json")
    logger1.debug("Діагностика")

    print("\nЗміна форматера на COLOR:")
    logger1.set_formatter("color")
    logger1.info("Кольорове повідомлення")

    print(f"\nФорматери: {FormatterFactory.available()}")
    print(f"Історія: {len(logger1.get_history())} записів")


if __name__ == "__main__":
    main()
