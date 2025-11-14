from typing import Protocol

from src.domain.models import Answer, Question, Todo


class PasswordManager(Protocol):
    def hash(self, password: str) -> str:
        ...

    def verify(self, password: str, password_hash: str) -> bool:
        ...


class TodoRepository(Protocol):
    async def add(self, todo: Todo) -> Todo:
        ...

    async def get_list(self, skip: int = 0, limit: int = 10) -> tuple[list[Todo], int]:
        ...

    async def get_deleted_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Todo], int]:
        ...

    async def get(self, todo_id: str) -> Todo | None:
        ...

    async def get_any(self, todo_id: str) -> Todo | None:
        ...

    async def update(self, todo: Todo) -> Todo:
        ...

    async def delete(self, todo_id: str) -> None:
        ...

    async def hard_delete(self, todo_id: str) -> None:
        ...


class QuestionRepository(Protocol):
    async def add(self, question: Question) -> Question:
        ...

    async def get_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Question], int]:
        ...

    async def get_deleted_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Question], int]:
        ...

    async def get(self, question_id: str) -> Question | None:
        ...

    async def get_any(self, question_id: str) -> Question | None:
        ...

    async def update(self, question: Question) -> Question:
        ...

    async def delete(self, question_id: str) -> None:
        ...

    async def hard_delete(self, question_id: str) -> None:
        ...


class AnswerRepository(Protocol):
    async def add(self, answer: Answer) -> Answer:
        ...

    async def get_deleted_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Answer], int]:
        ...

    async def get(self, answer_id: str) -> Answer | None:
        ...

    async def get_any(self, answer_id: str) -> Answer | None:
        ...

    async def update(self, answer: Answer) -> Answer:
        ...

    async def delete(self, answer_id: str) -> None:
        ...

    async def hard_delete(self, answer_id: str) -> None:
        ...


class UnitOfWork(Protocol):
    todo_repo: TodoRepository
    question_repo: QuestionRepository
    answer_repo: AnswerRepository

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    async def commit(self):
        ...

    async def rollback(self):
        ...
