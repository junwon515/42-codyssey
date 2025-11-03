from src.domain.exceptions import EmptyTaskError
from src.domain.models import Todo
from src.domain.ports import TodoRepository


class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def get_all_todos(self) -> list[Todo]:
        return self.repository.get_all()

    def create_todo(self, *, task: str | None, due_date: str | None) -> Todo:
        if not task:
            raise EmptyTaskError('Task cannot be empty.')

        new_todo = Todo(task=task, due_date=due_date)
        self.repository.add(new_todo)

        return new_todo
