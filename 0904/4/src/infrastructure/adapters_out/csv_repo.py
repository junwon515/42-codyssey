import csv
import os

from src.domain.models import Todo

CSV_FILE = 'todo_data.csv'
FIELDNAMES = ['id', 'task', 'due_date', 'is_completed']


class CsvTodoRepository:
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
                print(f'Error initializing CSV: {e}')

    def get_all(self) -> list[Todo]:
        todos = []
        try:
            with open(self.filepath, newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    todo = Todo(
                        id=row['id'],
                        task=row['task'],
                        due_date=row['due_date'] or None,
                        is_completed=(row['is_completed'] == 'True'),
                    )
                    todos.append(todo)
        except Exception as e:
            print(f'Error reading CSV: {e}')
            return []
        return todos

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
            print(f'Error writing to CSV: {e}')
