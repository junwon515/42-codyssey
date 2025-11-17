from datetime import UTC, datetime

from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from src.domain.entity import Answer, Question, Todo
from src.domain.exceptions import NotFoundError, PersistenceError
from src.domain.repos import AnswerRepository, QuestionRepository, TodoRepository
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

    async def get_list(self, skip: int = 0, limit: int = 10) -> tuple[list[Todo], int]:
        count_query = select(func.count(TodoTable.id)).where(
            TodoTable.deleted_at.is_(None)
        )
        total_items_result = await self.session.execute(count_query)
        total_items = total_items_result.scalar_one()

        query = (
            select(TodoTable)
            .where(TodoTable.deleted_at.is_(None))
            .order_by(TodoTable.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        all_todos_table = result.scalars().all()

        return [TodoMapper.to_domain(t) for t in all_todos_table], total_items

    async def get_deleted_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Todo], int]:
        count_query = select(func.count(TodoTable.id)).where(
            TodoTable.deleted_at.is_not(None)
        )
        total_items_result = await self.session.execute(count_query)
        total_items = total_items_result.scalar_one()

        query = (
            select(TodoTable)
            .where(TodoTable.deleted_at.is_not(None))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        all_todos_table = result.scalars().all()

        return [TodoMapper.to_domain(t) for t in all_todos_table], total_items

    async def get(self, todo_id: str) -> Todo | None:
        query = select(TodoTable).where(
            TodoTable.id == todo_id, TodoTable.deleted_at.is_(None)
        )
        result = await self.session.execute(query)
        todo_table = result.scalars().first()

        if todo_table:
            return TodoMapper.to_domain(todo_table)
        return None

    async def get_any(self, todo_id: str) -> Todo | None:
        todo_table = await self.session.get(TodoTable, todo_id)
        if todo_table:
            return TodoMapper.to_domain(todo_table)
        return None

    async def update(self, todo: Todo) -> Todo:
        try:
            todo_table = await self.session.get(TodoTable, todo.id)
            if todo_table and todo_table.deleted_at is None:
                TodoMapper.update_table_from_domain(todo, todo_table)
                await self.session.flush()
                await self.session.refresh(todo_table)
                return TodoMapper.to_domain(todo_table)
            raise NotFoundError(f'Todo with id {todo.id} not found.')
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise PersistenceError(original_exception=e)

    async def delete(self, todo_id: str) -> None:
        try:
            stmt = (
                update(TodoTable)
                .where(TodoTable.id == todo_id, TodoTable.deleted_at.is_(None))
                .values(deleted_at=datetime.now(UTC))
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                exists = await self.session.get(TodoTable, todo_id)
                if exists is None:
                    raise NotFoundError(f'Todo with id {todo_id} not found.')
            await self.session.flush()
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise PersistenceError(original_exception=e)

    async def hard_delete(self, todo_id: str) -> None:
        try:
            todo_table = await self.session.get(TodoTable, todo_id)
            if todo_table:
                await self.session.delete(todo_table)
                await self.session.flush()
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
            await self.session.refresh(question_table)
            return QuestionMapper.to_domain(question_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)

    async def get_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Question], int]:
        count_query = select(func.count(QuestionTable.id)).where(
            QuestionTable.deleted_at.is_(None)
        )
        total_items_result = await self.session.execute(count_query)
        total_items = total_items_result.scalar_one()

        query = (
            select(QuestionTable)
            .where(QuestionTable.deleted_at.is_(None))
            .order_by(QuestionTable.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        all_questions_table = result.scalars().all()

        return [QuestionMapper.to_domain(q) for q in all_questions_table], total_items

    async def get_deleted_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Question], int]:
        count_query = select(func.count(QuestionTable.id)).where(
            QuestionTable.deleted_at.is_not(None)
        )
        total_items_result = await self.session.execute(count_query)
        total_items = total_items_result.scalar_one()

        query = (
            select(QuestionTable)
            .where(QuestionTable.deleted_at.is_not(None))
            .order_by(QuestionTable.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        all_questions_table = result.scalars().all()

        return [QuestionMapper.to_domain(q) for q in all_questions_table], total_items

    async def get(self, question_id: str) -> Question | None:
        query = (
            select(QuestionTable)
            .where(QuestionTable.id == question_id, QuestionTable.deleted_at.is_(None))
            .options(
                selectinload(QuestionTable.answers).selectinload(AnswerTable.replies)
            )
        )
        result = await self.session.execute(query)
        question_table = result.scalars().first()

        if question_table:
            return QuestionMapper.to_domain(question_table)
        return None

    async def get_any(self, question_id: str) -> Question | None:
        query = (
            select(QuestionTable)
            .where(QuestionTable.id == question_id)
            .options(
                selectinload(QuestionTable.answers).selectinload(AnswerTable.replies)
            )
        )
        result = await self.session.execute(query)
        question_table = result.scalars().first()

        if question_table:
            return QuestionMapper.to_domain(question_table)
        return None

    async def update(self, question: Question) -> Question:
        try:
            question_table = await self.session.get(QuestionTable, question.id)
            if question_table and question_table.deleted_at is None:
                QuestionMapper.update_table_from_domain(question, question_table)
                await self.session.flush()
                await self.session.refresh(question_table)
                return QuestionMapper.to_domain(question_table)
            raise NotFoundError(f'Question with id {question.id} not found.')
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise PersistenceError(original_exception=e)

    async def delete(self, question_id: str) -> None:
        try:
            stmt = (
                update(QuestionTable)
                .where(
                    QuestionTable.id == question_id, QuestionTable.deleted_at.is_(None)
                )
                .values(deleted_at=datetime.now(UTC))
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                exists = await self.session.get(QuestionTable, question_id)
                if exists is None:
                    raise NotFoundError(f'Question with id {question_id} not found.')
            await self.session.flush()
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise PersistenceError(original_exception=e)

    async def hard_delete(self, question_id: str) -> None:
        try:
            question_table = await self.session.get(QuestionTable, question_id)
            if question_table:
                await self.session.delete(question_table)
                await self.session.flush()
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
            await self.session.refresh(answer_table)
            return AnswerMapper.to_domain(answer_table)
        except Exception as e:
            raise PersistenceError(original_exception=e)

    async def get_deleted_list(
        self, skip: int = 0, limit: int = 10
    ) -> tuple[list[Answer], int]:
        count_query = select(func.count(AnswerTable.id)).where(
            AnswerTable.deleted_at.is_not(None)
        )
        total_items_result = await self.session.execute(count_query)
        total_items = total_items_result.scalar_one()

        query = (
            select(AnswerTable)
            .where(AnswerTable.deleted_at.is_not(None))
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(query)
        all_answers_table = result.scalars().all()

        return [AnswerMapper.to_domain(t) for t in all_answers_table], total_items

    async def get(self, answer_id: str) -> Answer | None:
        query = (
            select(AnswerTable)
            .where(AnswerTable.id == answer_id, AnswerTable.deleted_at.is_(None))
            .options(selectinload(AnswerTable.replies))
        )
        result = await self.session.execute(query)
        answer_table = result.scalars().first()

        if answer_table:
            return AnswerMapper.to_domain(answer_table)
        return None

    async def get_any(self, answer_id: str) -> Answer | None:
        query = (
            select(AnswerTable)
            .where(AnswerTable.id == answer_id)
            .options(selectinload(AnswerTable.replies))
        )
        result = await self.session.execute(query)
        answer_table = result.scalars().first()

        if answer_table:
            return AnswerMapper.to_domain(answer_table)
        return None

    async def update(self, answer: Answer) -> Answer:
        try:
            answer_table = await self.session.get(AnswerTable, answer.id)
            if answer_table and answer_table.deleted_at is None:
                AnswerMapper.update_table_from_domain(answer, answer_table)
                await self.session.flush()
                await self.session.refresh(answer_table)
                return AnswerMapper.to_domain(answer_table)
            raise NotFoundError(f'Answer with id {answer.id} not found.')
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise PersistenceError(original_exception=e)

    async def delete(self, answer_id: str) -> None:
        try:
            stmt = (
                update(AnswerTable)
                .where(AnswerTable.id == answer_id, AnswerTable.deleted_at.is_(None))
                .values(deleted_at=datetime.now(UTC))
            )
            result = await self.session.execute(stmt)
            if result.rowcount == 0:
                exists = await self.session.get(AnswerTable, answer_id)
                if exists is None:
                    raise NotFoundError(f'Answer with id {answer_id} not found.')
            await self.session.flush()
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise PersistenceError(original_exception=e)

    async def hard_delete(self, answer_id: str) -> None:
        try:
            answer_table = await self.session.get(AnswerTable, answer_id)
            if answer_table:
                await self.session.delete(answer_table)
                await self.session.flush()
        except Exception as e:
            raise PersistenceError(original_exception=e)
