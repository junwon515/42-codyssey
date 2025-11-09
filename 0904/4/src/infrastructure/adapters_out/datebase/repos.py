from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.domain.exceptions import PersistenceError
from src.domain.models import Answer, Question, Todo
from src.domain.ports import AnswerRepository, QuestionRepository, TodoRepository
from src.infrastructure.adapters_out.datebase.daos import (
    AnswerTable,
    QuestionTable,
    TodoTable,
)
from src.infrastructure.adapters_out.datebase.mappers import (
    AnswerMapper,
    QuestionMapper,
    TodoMapper,
)


class SqlAlchemyTodoRepository(TodoRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, todo: Todo) -> Todo:
        try:
            todo_table = TodoMapper.to_table(todo)
            self.session.add(todo_table)
            await self.session.flush()
            return TodoMapper.to_domain(todo_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)

    async def get_all(self) -> list[Todo]:
        query = select(TodoTable)
        result = await self.session.execute(query)
        all_todos_table = result.scalars().all()
        return [TodoMapper.to_domain(t) for t in all_todos_table]

    async def get(self, todo_id: str) -> Todo | None:
        todo_table = await self.session.get(TodoTable, todo_id)
        if todo_table:
            return TodoMapper.to_domain(todo_table)
        return None

    async def update(self, todo: Todo) -> Todo:
        try:
            todo_table = await self.session.get(TodoTable, todo.id)
            if todo_table:
                TodoMapper.update_table_from_domain(todo, todo_table)
                await self.session.flush()
                return TodoMapper.to_domain(todo_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)

    async def delete(self, todo_id: str) -> None:
        try:
            todo_table = await self.session.get(TodoTable, todo_id)
            if todo_table:
                await self.session.delete(todo_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)


class SqlAlchemyQuestionRepository(QuestionRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, question: Question) -> Question:
        try:
            question_table = QuestionMapper.to_table(question)
            self.session.add(question_table)
            await self.session.flush()
            return QuestionMapper.to_domain(question_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)

    async def get_all(self) -> list[Question]:
        query = select(QuestionTable).options(selectinload(QuestionTable.answers))
        result = await self.session.execute(query)
        all_questions_table = result.scalars().unique().all()
        return [QuestionMapper.to_domain(q) for q in all_questions_table]

    async def get(self, question_id: str) -> Question | None:
        query = (
            select(QuestionTable)
            .where(QuestionTable.id == question_id)
            .options(selectinload(QuestionTable.answers))
        )
        result = await self.session.execute(query)
        question_table = result.scalars().first()

        if question_table:
            return QuestionMapper.to_domain(question_table)
        return None

    async def update(self, question: Question) -> Question:
        try:
            question_table = await self.session.get(QuestionTable, question.id)
            if question_table:
                QuestionMapper.update_table_from_domain(question, question_table)
                await self.session.flush()
                return QuestionMapper.to_domain(question_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)

    async def delete(self, question_id: str) -> None:
        try:
            question_table = await self.session.get(QuestionTable, question_id)
            if question_table:
                await self.session.delete(question_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)


class SqlAlchemyAnswerRepository(AnswerRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, answer: Answer) -> Answer:
        try:
            answer_table = AnswerMapper.to_table(answer)
            self.session.add(answer_table)
            await self.session.flush()
            return AnswerMapper.to_domain(answer_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)

    async def get(self, answer_id: str) -> Answer | None:
        answer_table = await self.session.get(AnswerTable, answer_id)
        if answer_table:
            return AnswerMapper.to_domain(answer_table)
        return None

    async def update(self, answer: Answer) -> Answer:
        try:
            answer_table = await self.session.get(AnswerTable, answer.id)
            if answer_table:
                AnswerMapper.update_table_from_domain(answer, answer_table)
                await self.session.flush()
                return AnswerMapper.to_domain(answer_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)

    async def delete(self, answer_id: str) -> None:
        try:
            answer_table = await self.session.get(AnswerTable, answer_id)
            if answer_table:
                await self.session.delete(answer_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)
