"""Декоратори функцій з параметрами."""

import functools
import time


def cache(max_size: int = 128):
    """Декоратор кешування результатів функції."""

    def decorator(func):
        _cache = {}
        _call_order = []

        @functools.wraps(func)
        def wrapper(*args):
            if args in _cache:
                print(f"cache hit: {func.__name__}{args}")
                return _cache[args]

            print(f"cache miss: {func.__name__}{args}")
            result = func(*args)
            _cache[args] = result
            _call_order.append(args)

            if len(_cache) > max_size:
                oldest_key = _call_order.pop(0)
                _cache.pop(oldest_key, None)

            return result

        wrapper.cache_info = lambda: {"size": len(_cache), "max_size": max_size}
        wrapper.cache_clear = lambda: (_cache.clear(), _call_order.clear())
        return wrapper

    return decorator


def rate_limit(max_calls: int, period: float = 60.0):
    """Декоратор обмеження частоти викликів функції."""

    def decorator(func):
        call_times = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_time = time.time()
            call_times[:] = [t for t in call_times if current_time - t < period]

            if len(call_times) >= max_calls:
                raise RuntimeError(
                    f"Перевищено ліміт: максимум {max_calls} викликів за {period} секунд"
                )

            call_times.append(current_time)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log(level: str = "INFO"):
    """Декоратор логування виклику функції з зазначенням рівня."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[{level}] Виклик {func.__name__}(args={args}, kwargs={kwargs})")
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as error:
                elapsed = time.perf_counter() - start
                print(f"[ERROR] {func.__name__} завершилась помилкою: {error} (час: {elapsed:.6f}с)")
                raise
            elapsed = time.perf_counter() - start
            print(f"[{level}] {func.__name__} → {result} (час: {elapsed:.6f}с)")
            return result

        return wrapper

    return decorator


@cache(max_size=64)
def fibonacci(n: int) -> int:
    """Обчислює n-е число Фібоначчі рекурсивно."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@rate_limit(max_calls=5, period=10.0)
def send_notification(message: str) -> str:
    """Імітує відправку сповіщення."""
    return f"Надіслано: {message}"


@log(level="DEBUG")
def divide(a: float, b: float) -> float:
    """Ділення з можливим ZeroDivisionError."""
    return a / b


def main():
    print("Обчислення Fibonacci:")
    print(f"fibonacci(10) = {fibonacci(10)}")
    print(f"cache_info = {fibonacci.cache_info()}")

    print("\nПеревірка rate_limit:")
    for i in range(6):
        try:
            print(send_notification(f"Повідомлення {i + 1}"))
        except RuntimeError as error:
            print(f"Очікувана помилка: {error}")

    print("\nПеревірка log:")
    divide(10, 3)
    try:
        divide(10, 0)
    except ZeroDivisionError:
        print("Помилку ділення на нуль оброблено у main()")


if __name__ == "__main__":
    main()
