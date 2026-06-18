"""Система плагінів з автоматичною реєстрацією через метаклас."""

from abc import abstractmethod
import hashlib


class PluginMeta(type):
    """Метаклас для автоматичної реєстрації та валідації плагінів."""

    _registry: dict[str, type] = {}
    REQUIRED_ATTRS = ("name", "version")

    def __new__(mcs, cls_name: str, bases: tuple, namespace: dict):
        cls = super().__new__(mcs, cls_name, bases, namespace)

        if bases:
            for attr in mcs.REQUIRED_ATTRS:
                if attr not in namespace:
                    raise TypeError(
                        f"Клас {cls_name} повинен містити обов'язковий атрибут '{attr}'"
                    )

            plugin_name = namespace["name"]
            if not isinstance(plugin_name, str) or not plugin_name:
                raise TypeError("Атрибут 'name' повинен бути непорожнім рядком")

            mcs._registry[plugin_name] = cls

        return cls

    @classmethod
    def get_registry(mcs) -> dict[str, type]:
        """Повертає копію реєстру плагінів."""
        return mcs._registry.copy()

    @classmethod
    def create_plugin(mcs, plugin_name: str):
        """Фабричний метод: створює екземпляр плагіна за його name."""
        if plugin_name not in mcs._registry:
            raise ValueError(f"Плагін '{plugin_name}' не знайдено")
        return mcs._registry[plugin_name]()


class BasePlugin(metaclass=PluginMeta):
    """Базовий клас плагіна."""

    @abstractmethod
    def execute(self, data: str) -> str:
        """Обробити вхідні дані."""
        raise NotImplementedError


class UpperPlugin(BasePlugin):
    """Плагін для перетворення тексту у верхній регістр."""

    name = "upper"
    version = "1.0"

    def execute(self, data: str) -> str:
        return data.upper()


class ReversePlugin(BasePlugin):
    """Плагін для розвертання тексту."""

    name = "reverse"
    version = "1.0"

    def execute(self, data: str) -> str:
        return data[::-1]


class CensorPlugin(BasePlugin):
    """Плагін для заміни заданих слів на ***."""

    name = "censor"
    version = "1.1"

    def execute(self, data: str) -> str:
        banned_words = ["погано", "bad", "Світ"]
        result = data
        for word in banned_words:
            result = result.replace(word, "***")
        return result


def hash_execute(self, data: str) -> str:
    """Повертає SHA-256 хеш рядка."""
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


HashPlugin = type(
    "HashPlugin",
    (BasePlugin,),
    {
        "name": "hash",
        "version": "2.0",
        "execute": hash_execute,
        "__doc__": "Плагін для створення хешу рядка.",
    },
)


def main():
    print("Зареєстровані плагіни:")
    for name, cls in PluginMeta.get_registry().items():
        print(f"  {name} (v{cls.version}): {cls.__name__}")

    print("\nРобота плагінів:")
    test_data = "Привіт Світ"
    for name in PluginMeta.get_registry():
        plugin = PluginMeta.create_plugin(name)
        print(f"  {name}: {plugin.execute(test_data)}")

    print("\nПеревірка помилки валідації:")
    try:
        type(
            "BrokenPlugin",
            (BasePlugin,),
            {
                "name": "broken",
                "execute": lambda self, data: data,
            },
        )
    except TypeError as error:
        print(f"  Очікувана помилка: {error}")


if __name__ == "__main__":
    main()
