from fastapi import Depends

from src.application.services import TodoService
from src.domain.ports import TodoRepository
from src.infrastructure.adapters_out.csv_repo import CsvTodoRepository


def get_todo_repo() -> TodoRepository:
    return CsvTodoRepository(filepath='todo_data.csv')


def get_todo_service(repo: TodoRepository = Depends(get_todo_repo)) -> TodoService:
    return TodoService(repository=repo)
