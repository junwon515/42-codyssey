from typing import Protocol

from .models import Todo


class TodoRepository(Protocol):
    def add(self, todo: Todo) -> None:
        ...

    def get_all(self) -> list[Todo]:
        ...
