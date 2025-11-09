from datetime import date

from src.domain.exceptions import EmptyTaskError, NotFoundError
from src.domain.models import Answer, Question, Todo
from src.domain.ports import UnitOfWork


class TodoService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_todo(self, *, task: str | None, due_date: date | None) -> Todo:
        if not task:
            raise EmptyTaskError('Task cannot be empty.')
        new_todo = Todo(task=task, due_date=due_date)
        return await self.uow.todos.add(new_todo)

    async def get_all_todos(self) -> list[Todo]:
        return await self.uow.todos.get_all()

    async def get_todo(self, *, todo_id: str) -> Todo:
        todo = await self.uow.todos.get(todo_id)
        if todo is None:
            raise NotFoundError(f'Todo with id {todo_id} not found.')
        return todo

    async def update_todo(
        self, *, todo_id: str, task: str, due_date: date | None
    ) -> Todo:
        todo = await self.get_todo(todo_id=todo_id)
        todo.update(task=task, due_date=due_date)
        return await self.uow.todos.update(todo)

    async def delete_todo(self, *, todo_id: str) -> None:
        await self.get_todo(todo_id=todo_id)
        return await self.uow.todos.delete(todo_id)


class QuestionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_question(self, *, subject: str, content: str) -> Question:
        new_question = Question(subject=subject, content=content)
        return await self.uow.questions.add(new_question)

    async def get_all_questions(self) -> list[Question]:
        return await self.uow.questions.get_all()

    async def get_question(self, *, question_id: str) -> Question:
        question = await self.uow.questions.get(question_id)
        if question is None:
            raise NotFoundError(f'Question with id {question_id} not found.')
        return question

    async def update_question(
        self, *, question_id: str, subject: str, content: str
    ) -> Question:
        question = await self.get_question(question_id=question_id)
        question.update(subject=subject, content=content)
        return await self.uow.questions.update(question)

    async def delete_question(self, *, question_id: str) -> None:
        await self.get_question(question_id=question_id)
        return await self.uow.questions.delete(question_id)


class AnswerService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def create_answer(self, *, question_id: str, content: str) -> Answer:
        question = await self.uow.questions.get(question_id)
        if question is None:
            raise NotFoundError(f'Question with id {question_id} not found.')
        new_answer = Answer(content=content, question_id=question_id)
        return await self.uow.answers.add(new_answer)

    async def get_answer(self, *, answer_id: str) -> Answer:
        answer = await self.uow.answers.get(answer_id)
        if answer is None:
            raise NotFoundError(f'Answer with id {answer_id} not found.')
        return answer

    async def update_answer(self, *, answer_id: str, content: str) -> Answer:
        answer = await self.get_answer(answer_id=answer_id)
        answer.update(content=content)
        return await self.uow.answers.update(answer)

    async def delete_answer(self, *, answer_id: str) -> None:
        await self.get_answer(answer_id=answer_id)
        return await self.uow.answers.delete(answer_id)
