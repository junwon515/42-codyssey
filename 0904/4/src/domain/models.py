import uuid
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Todo:
    task: str
    due_date: date | None = None
    is_completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def complete(self) -> None:
        self.is_completed = True

    def update(self, task: str, due_date: date | None) -> None:
        self.task = task
        self.due_date = due_date


@dataclass
class Question:
    subject: str
    content: str
    create_date: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    answers: list['Answer'] = field(default_factory=list)

    def update(self, subject: str, content: str) -> None:
        self.subject = subject
        self.content = content


@dataclass
class Answer:
    content: str
    question_id: str
    create_date: datetime | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def update(self, content: str) -> None:
        self.content = content
