from datetime import date

from src.domain.exceptions import EmptyTaskError, NotFoundError
from src.domain.models import Todo
from src.domain.ports import TodoRepository


class TodoService:
    def __init__(self, repository: TodoRepository):
        self.repository = repository

    def create_todo(self, *, task: str | None, due_date: date | None) -> Todo:
        if not task:
            raise EmptyTaskError('Task cannot be empty.')
        new_todo = Todo(task=task, due_date=due_date)
        self.repository.add(new_todo)
        return new_todo

    def get_all_todos(self) -> list[Todo]:
        return self.repository.get_all()

    def get_todo(self, *, todo_id: str) -> Todo:
        todo = self.repository.get(todo_id)
        if todo is None:
            raise NotFoundError(f'Todo with id {todo_id} not found.')
        return todo

    def update_todo(self, *, todo_id: str, task: str, due_date: date | None) -> Todo:
        todo = self.get_todo(todo_id=todo_id)
        todo.update(task=task, due_date=due_date)
        self.repository.update(todo)
        return todo

    def delete_todo(self, *, todo_id: str) -> None:
        todo = self.get_todo(todo_id=todo_id)
        self.repository.delete(todo.id)
        return None
