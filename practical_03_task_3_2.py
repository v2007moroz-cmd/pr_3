"""Паттерни Observer, Strategy та архітектурний шаблон MVC."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Callable


class EventEmitter:
    """Базовий клас для підтримки системи подій Observer."""

    def __init__(self):
        self._listeners: dict[str, list[Callable]] = {}

    def on(self, event: str, callback: Callable):
        """Підписатися на подію."""
        self._listeners.setdefault(event, []).append(callback)

    def off(self, event: str, callback: Callable):
        """Відписатися від події."""
        if event in self._listeners and callback in self._listeners[event]:
            self._listeners[event].remove(callback)

    def emit(self, event: str, *args, **kwargs):
        """Сповістити всіх слухачів про подію."""
        for callback in self._listeners.get(event, []):
            callback(*args, **kwargs)


class SortStrategy(ABC):
    """Абстрактна стратегія сортування завдань."""

    @abstractmethod
    def sort(self, tasks: list["Task"]) -> list["Task"]:
        raise NotImplementedError


class SortByPriority(SortStrategy):
    """Сортування за пріоритетом: 1 — найвищий, 5 — найнижчий."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda task: task.priority)


class SortByDeadline(SortStrategy):
    """Сортування за терміном виконання."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda task: task.deadline)


class SortByCreationDate(SortStrategy):
    """Сортування за датою створення: найновіші першими."""

    def sort(self, tasks: list["Task"]) -> list["Task"]:
        return sorted(tasks, key=lambda task: task.created_at, reverse=True)


@dataclass
class Task:
    title: str
    priority: int
    deadline: datetime
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)


class TaskModel(EventEmitter):
    """Model: дані та бізнес-логіка завдань."""

    def __init__(self):
        super().__init__()
        self._tasks: list[Task] = []

    def add_task(self, title: str, priority: int, deadline: datetime):
        if not 1 <= priority <= 5:
            raise ValueError("Пріоритет повинен бути від 1 до 5")
        task = Task(title=title, priority=priority, deadline=deadline)
        self._tasks.append(task)
        self.emit("task_added", task)

    def complete_task(self, index: int):
        task = self._tasks[index]
        task.completed = True
        self.emit("task_completed", task)

    def remove_task(self, index: int):
        task = self._tasks.pop(index)
        self.emit("task_removed", task)

    def get_tasks(self, include_completed: bool = True) -> list[Task]:
        if include_completed:
            return self._tasks[:]
        return [task for task in self._tasks if not task.completed]

    def get_statistics(self) -> dict:
        total = len(self._tasks)
        completed = sum(1 for task in self._tasks if task.completed)
        return {
            "total": total,
            "completed": completed,
            "active": total - completed,
        }


class TaskView:
    """View: відображення даних у консолі."""

    def show_tasks(self, tasks: list[Task], title: str = "Завдання"):
        print(f"\n{title}")
        print("-" * 78)
        print(f"{'№':<4}{'Назва':<28}{'Пріоритет':<12}{'Дедлайн':<18}{'Статус':<12}")
        print("-" * 78)
        for index, task in enumerate(tasks, start=1):
            status = "виконано" if task.completed else "активне"
            deadline = task.deadline.strftime("%Y-%m-%d %H:%M")
            print(f"{index:<4}{task.title:<28}{task.priority:<12}{deadline:<18}{status:<12}")
        print("-" * 78)

    def show_message(self, message: str):
        print(f"[INFO] {message}")

    def show_statistics(self, stats: dict):
        print("\nСтатистика:")
        print(f"  Усього: {stats['total']}")
        print(f"  Виконано: {stats['completed']}")
        print(f"  Активних: {stats['active']}")


class TaskController:
    """Controller: координація Model та View з підтримкою Strategy."""

    def __init__(self, model: TaskModel, view: TaskView):
        self._model = model
        self._view = view
        self._sort_strategy: SortStrategy = SortByPriority()

        self._model.on("task_added", lambda task: self._view.show_message(f"Додано завдання: {task.title}"))
        self._model.on("task_completed", lambda task: self._view.show_message(f"Завдання виконано: {task.title}"))
        self._model.on("task_removed", lambda task: self._view.show_message(f"Видалено завдання: {task.title}"))

    def set_sort_strategy(self, strategy: SortStrategy):
        """Змінити стратегію сортування."""
        self._sort_strategy = strategy

    def add_task(self, title: str, priority: int, deadline: datetime):
        self._model.add_task(title, priority, deadline)

    def complete_task(self, index: int):
        self._model.complete_task(index)

    def remove_task(self, index: int):
        self._model.remove_task(index)

    def show_all(self):
        tasks = self._model.get_tasks()
        sorted_tasks = self._sort_strategy.sort(tasks)
        self._view.show_tasks(sorted_tasks)

    def show_active(self):
        tasks = self._model.get_tasks(include_completed=False)
        sorted_tasks = self._sort_strategy.sort(tasks)
        self._view.show_tasks(sorted_tasks, title="Активні завдання")

    def show_stats(self):
        self._view.show_statistics(self._model.get_statistics())


def main():
    model = TaskModel()
    view = TaskView()
    ctrl = TaskController(model, view)

    now = datetime.now()
    ctrl.add_task("Підготувати звіт", 1, now + timedelta(days=1))
    ctrl.add_task("Вивчити патерни", 2, now + timedelta(days=3))
    ctrl.add_task("Оновити README", 4, now + timedelta(days=2))
    ctrl.add_task("Зробити скріншоти", 3, now + timedelta(hours=12))
    ctrl.add_task("Завантажити на GitHub", 1, now + timedelta(days=4))

    print("\nСортування за пріоритетом:")
    ctrl.set_sort_strategy(SortByPriority())
    ctrl.show_all()

    print("\nСортування за дедлайном:")
    ctrl.set_sort_strategy(SortByDeadline())
    ctrl.show_all()

    print("\nСортування за датою створення:")
    ctrl.set_sort_strategy(SortByCreationDate())
    ctrl.show_all()

    ctrl.complete_task(0)
    ctrl.show_active()
    ctrl.show_stats()


if __name__ == "__main__":
    main()
