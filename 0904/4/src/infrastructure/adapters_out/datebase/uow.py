from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from src.domain.repos import UnitOfWork
from src.infrastructure.adapters_out.datebase.repos import (
    SqlAlchemyAnswerRepository,
    SqlAlchemyQuestionRepository,
    SqlAlchemyTodoRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory
        self.session: AsyncSession | None = None

    async def __aenter__(self):
        self.session = self.session_factory()
        self.todo_repo = SqlAlchemyTodoRepository(self.session)
        self.question_repo = SqlAlchemyQuestionRepository(self.session)
        self.answer_repo = SqlAlchemyAnswerRepository(self.session)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
            await self.session.close()

    async def commit(self):
        if self.session:
            await self.session.commit()

    async def rollback(self):
        if self.session:
            await self.session.rollback()
