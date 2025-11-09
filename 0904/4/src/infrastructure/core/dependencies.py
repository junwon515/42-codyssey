from collections.abc import AsyncGenerator

from fastapi import Depends

from src.application.services import AnswerService, QuestionService, TodoService
from src.domain.ports import UnitOfWork
from src.infrastructure.adapters_out.datebase.uow import SqlAlchemyUnitOfWork
from src.infrastructure.core.database import AsyncSessionLocal


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    uow = SqlAlchemyUnitOfWork(AsyncSessionLocal)

    async with uow:
        try:
            yield uow
        except Exception:
            raise


def get_todo_service(uow: UnitOfWork = Depends(get_uow)) -> TodoService:
    return TodoService(uow=uow)


def get_question_service(uow: UnitOfWork = Depends(get_uow)) -> QuestionService:
    return QuestionService(uow=uow)


def get_answer_service(uow: UnitOfWork = Depends(get_uow)) -> AnswerService:
    return AnswerService(uow=uow)
