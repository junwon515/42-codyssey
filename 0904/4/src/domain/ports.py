from typing import Protocol

from .models import Todo


class TodoRepository(Protocol):
    def add(self, todo: Todo) -> None:
        ...

    def get_all(self) -> list[Todo]:
        ...

    def get(self, todo_id: str) -> Todo | None:
        ...

    def update(self, todo: Todo) -> None:
        ...

    def delete(self, todo_id: str) -> None:
        ...
