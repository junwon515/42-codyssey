import uuid
from dataclasses import dataclass, field
from datetime import date, datetime


@dataclass
class Todo:
    task: str
    creator_ip: str
    password_hash: str
    due_date: date | None = None
    is_completed: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def complete(self) -> None:
        self.is_completed = True

    def uncomplete(self) -> None:
        self.is_completed = False

    def update(self, task: str, due_date: date | None) -> None:
        self.task = task
        self.due_date = due_date


@dataclass
class Question:
    subject: str
    content: str
    creator_ip: str
    password_hash: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime | None = None
    updated_at: datetime | None = None
    answers: list['Answer'] = field(default_factory=list)
    answer_count: int = 0

    def update(self, subject: str, content: str) -> None:
        self.subject = subject
        self.content = content


@dataclass
class Answer:
    content: str
    question_id: str
    creator_ip: str
    password_hash: str
    parent_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: datetime | None = None
    replies: list['Answer'] = field(default_factory=list)
    reply_count: int = 0

    def update(self, content: str) -> None:
        self.content = content
