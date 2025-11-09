import csv
import os
from datetime import datetime

from src.domain.exceptions import InfrastructureError
from src.domain.models import Todo
from src.domain.ports import TodoRepository

CSV_FILE = 'todo_data.csv'
FIELDNAMES = ['id', 'task', 'due_date', 'is_completed']


class CsvTodoRepository(TodoRepository):
    def __init__(self, filepath: str = CSV_FILE):
        self.filepath = filepath
        self._initialize_file()

    def _initialize_file(self):
        if not os.path.exists(self.filepath):
            try:
                with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                    writer.writeheader()
            except OSError as e:
                raise InfrastructureError(
                    message='Failed to initialize CSV file.',
                    original_exception=e,
                )

    def _write_all(self, todos: list[Todo]) -> None:
        try:
            with open(self.filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                writer.writeheader()
                for todo in todos:
                    row = {
                        'id': todo.id,
                        'task': todo.task,
                        'due_date': todo.due_date,
                        'is_completed': todo.is_completed,
                    }
                    writer.writerow(row)
        except OSError as e:
            raise InfrastructureError(
                message='Failed to write to CSV file.',
                original_exception=e,
            )

    def add(self, todo: Todo) -> None:
        try:
            with open(self.filepath, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
                row = {
                    'id': todo.id,
                    'task': todo.task,
                    'due_date': todo.due_date,
                    'is_completed': todo.is_completed,
                }
                writer.writerow(row)
        except OSError as e:
            raise InfrastructureError(
                message='Failed to add todo to CSV file.',
                original_exception=e,
            )

    def get_all(self) -> list[Todo]:
        todos = []
        try:
            with open(self.filepath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    todo = Todo(
                        id=row['id'],
                        task=row['task'],
                        due_date=datetime.strptime(row['due_date'], '%Y-%m-%d').date()
                        if row['due_date']
                        else None,
                        is_completed=(row['is_completed'] == 'True'),
                    )
                    todos.append(todo)
        except Exception as e:
            raise InfrastructureError(
                message='Failed to read from CSV file.',
                original_exception=e,
            )
        return todos

    def get(self, todo_id: str) -> Todo | None:
        todos = self.get_all()
        for todo in todos:
            if todo.id == todo_id:
                return todo
        return None

    def update(self, todo: Todo) -> None:
        todos = self.get_all()
        for i, t in enumerate(todos):
            if t.id == todo.id:
                todos[i] = todo
                break
        self._write_all(todos)

    def delete(self, todo_id: str) -> None:
        todos = self.get_all()
        todos = [t for t in todos if t.id != todo_id]
        self._write_all(todos)
