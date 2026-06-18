"""Типізовані дескриптори та __init_subclass__ для системи конфігурації."""


class ValidatedField:
    """Дескриптор із валідацією типу та діапазону значень."""

    def __init__(self, expected_type: type, min_value=None, max_value=None):
        self.expected_type = expected_type
        self.min_value = min_value
        self.max_value = max_value
        self.name = ""
        self.private_name = ""

    def __set_name__(self, owner, name):
        self.name = name
        self.private_name = f"_{name}"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return getattr(obj, self.private_name)

    def __set__(self, obj, value):
        if not isinstance(value, self.expected_type):
            raise TypeError(
                f"Поле '{self.name}' повинно мати тип {self.expected_type.__name__}, "
                f"отримано {type(value).__name__}"
            )

        if self.min_value is not None and value < self.min_value:
            raise ValueError(
                f"Поле '{self.name}' повинно бути не менше {self.min_value}, отримано {value}"
            )

        if self.max_value is not None and value > self.max_value:
            raise ValueError(
                f"Поле '{self.name}' повинно бути не більше {self.max_value}, отримано {value}"
            )

        setattr(obj, self.private_name, value)


class ConfigSection:
    """Базовий клас секції конфігурації з автоматичною реєстрацією."""

    _sections: dict[str, type] = {}

    def __init_subclass__(cls, section_name: str = "", **kwargs):
        super().__init_subclass__(**kwargs)
        if section_name:
            cls._sections[section_name] = cls
            cls.section_name = section_name

    @classmethod
    def get_section(cls, name: str):
        """Повертає клас секції за іменем."""
        if name not in cls._sections:
            raise KeyError(f"Секцію '{name}' не знайдено")
        return cls._sections[name]

    @classmethod
    def list_sections(cls) -> list[str]:
        """Повертає список усіх зареєстрованих секцій."""
        return list(cls._sections.keys())


class DatabaseConfig(ConfigSection, section_name="database"):
    """Секція налаштувань бази даних."""

    host = ValidatedField(str)
    port = ValidatedField(int, min_value=1, max_value=65535)
    max_connections = ValidatedField(int, min_value=1, max_value=1000)

    def __init__(self, host: str, port: int, max_connections: int):
        self.host = host
        self.port = port
        self.max_connections = max_connections


class LoggingConfig(ConfigSection, section_name="logging"):
    """Секція налаштувань логування."""

    level = ValidatedField(str)
    max_file_size_mb = ValidatedField(int, min_value=1, max_value=1024)

    def __init__(self, level: str, max_file_size_mb: int):
        self.level = level
        self.max_file_size_mb = max_file_size_mb


def main():
    print("Зареєстровані секції:")
    print(ConfigSection.list_sections())

    print("\nКоректне створення DatabaseConfig:")
    db = DatabaseConfig("localhost", 5432, 100)
    print(f"  host={db.host}, port={db.port}, max_connections={db.max_connections}")

    print("\nКоректне створення LoggingConfig:")
    log_cfg = LoggingConfig("INFO", 100)
    print(f"  level={log_cfg.level}, max_file_size_mb={log_cfg.max_file_size_mb}")

    print("\nПеревірка TypeError:")
    try:
        db.port = "5432"
    except TypeError as error:
        print(f"  Очікувана помилка: {error}")

    print("\nПеревірка ValueError:")
    try:
        db.max_connections = 5000
    except ValueError as error:
        print(f"  Очікувана помилка: {error}")


if __name__ == "__main__":
    main()
