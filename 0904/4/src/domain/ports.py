from typing import Protocol

from .models import Answer, Question, Todo


class TodoRepository(Protocol):
    async def add(self, todo: Todo) -> Todo:
        ...

    async def get_all(self) -> list[Todo]:
        ...

    async def get(self, todo_id: str) -> Todo | None:
        ...

    async def update(self, todo: Todo) -> Todo:
        ...

    async def delete(self, todo_id: str) -> None:
        ...


class QuestionRepository(Protocol):
    async def add(self, question: Question) -> Question:
        ...

    async def get_all(self) -> list[Question]:
        ...

    async def get(self, question_id: str) -> Question | None:
        ...

    async def update(self, question: Question) -> Question:
        ...

    async def delete(self, question_id: str) -> None:
        ...


class AnswerRepository(Protocol):
    async def add(self, answer: Answer) -> Answer:
        ...

    async def get(self, answer_id: str) -> Answer | None:
        ...

    async def update(self, answer: Answer) -> Answer:
        ...

    async def delete(self, answer_id: str) -> None:
        ...


class UnitOfWork(Protocol):
    todos: TodoRepository
    questions: QuestionRepository
    answers: AnswerRepository

    async def __aenter__(self):
        ...

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        ...

    async def commit(self):
        ...

    async def rollback(self):
        ...
