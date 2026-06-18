"""Декоратори класів."""

import functools
import time


def auto_repr(cls):
    """Декоратор класу: додає __repr__ на основі __init__ параметрів."""
    init = cls.__init__
    params = init.__code__.co_varnames[1:init.__code__.co_argcount]

    def __repr__(self):
        values = ", ".join(f"{name}={getattr(self, name)!r}" for name in params)
        return f"{cls.__name__}({values})"

    cls.__repr__ = __repr__
    return cls


def frozen(cls):
    """Декоратор класу: забороняє зміну атрибутів після __init__."""
    original_init = cls.__init__
    original_setattr = cls.__setattr__

    @functools.wraps(original_init)
    def __init__(self, *args, **kwargs):
        original_setattr(self, "_frozen", False)
        original_init(self, *args, **kwargs)
        original_setattr(self, "_frozen", True)

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(f"Об'єкт {cls.__name__} є незмінним. Поле '{name}' змінити не можна")
        original_setattr(self, name, value)

    cls.__init__ = __init__
    cls.__setattr__ = __setattr__
    return cls


def log_methods(cls):
    """Декоратор класу: логує виклики всіх публічних методів."""

    def make_wrapper(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            print(f"[LOG] Виклик {cls.__name__}.{method.__name__}(args={args}, kwargs={kwargs})")
            start = time.perf_counter()
            try:
                result = method(self, *args, **kwargs)
            except Exception as error:
                elapsed = time.perf_counter() - start
                print(f"[LOG] Помилка в {method.__name__}: {error} (час: {elapsed:.6f}с)")
                raise
            elapsed = time.perf_counter() - start
            print(f"[LOG] Результат {method.__name__}: {result} (час: {elapsed:.6f}с)")
            return result

        return wrapper

    for name, value in list(cls.__dict__.items()):
        if callable(value) and not name.startswith("_"):
            setattr(cls, name, make_wrapper(value))

    return cls


@auto_repr
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@frozen
class ImmutableConfig:
    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug


@log_methods
class MathService:
    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Ділення на нуль")
        return a / b


def main():
    print("Перевірка @auto_repr:")
    p = Point(3.0, 4.0)
    print(repr(p))

    print("\nПеревірка @frozen:")
    cfg = ImmutableConfig("localhost", 8080, debug=True)
    print(f"Config: {cfg.host}:{cfg.port}, debug={cfg.debug}")
    try:
        cfg.host = "remote"
    except AttributeError as error:
        print(f"Очікувана помилка: {error}")

    print("\nПеревірка @log_methods:")
    svc = MathService()
    svc.add(10, 20)
    svc.multiply(3, 7)
    try:
        svc.divide(10, 0)
    except ValueError:
        print("Помилку ділення оброблено у main()")


if __name__ == "__main__":
    main()
