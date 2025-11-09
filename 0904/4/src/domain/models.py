import uuid
from dataclasses import dataclass, field
from datetime import date


@dataclass
class Todo:
    task: str
    due_date: date | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    is_completed: bool = False

    def complete(self) -> None:
        self.is_completed = True

    def update(self, task: str, due_date: date | None) -> None:
        self.task = task
        self.due_date = due_date
