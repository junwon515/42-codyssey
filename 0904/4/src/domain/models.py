import uuid
from dataclasses import dataclass, field


@dataclass
class Todo:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task: str
    due_date: str | None = None
    is_completed: bool = False

    def complete(self) -> None:
        self.is_completed = True
