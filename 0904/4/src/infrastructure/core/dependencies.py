from collections.abc import AsyncGenerator

from fastapi import Depends, Request

from src.application.services import (
    AdminService,
    AnswerService,
    QuestionService,
    TodoService,
)
from src.domain.exceptions import AuthorizationError
from src.domain.ports import PasswordManager, UnitOfWork
from src.infrastructure.adapters_out.datebase.uow import SqlAlchemyUnitOfWork
from src.infrastructure.adapters_out.password_manager import BcryptPasswordManager
from src.infrastructure.core.config import settings
from src.infrastructure.core.database import AsyncSessionLocal


async def get_uow() -> AsyncGenerator[UnitOfWork, None]:
    uow = SqlAlchemyUnitOfWork(AsyncSessionLocal)

    async with uow:
        try:
            yield uow
        except Exception:
            raise


def get_password_manager() -> PasswordManager:
    return BcryptPasswordManager()


def get_admin_service(uow: UnitOfWork = Depends(get_uow)) -> AdminService:
    return AdminService(uow=uow)


def get_todo_service(
    uow: UnitOfWork = Depends(get_uow),
    password_manager: PasswordManager = Depends(get_password_manager),
) -> TodoService:
    return TodoService(uow=uow, password_manager=password_manager)


def get_question_service(
    uow: UnitOfWork = Depends(get_uow),
    password_manager: PasswordManager = Depends(get_password_manager),
) -> QuestionService:
    return QuestionService(uow=uow, password_manager=password_manager)


def get_answer_service(
    uow: UnitOfWork = Depends(get_uow),
    password_manager: PasswordManager = Depends(get_password_manager),
) -> AnswerService:
    return AnswerService(uow=uow, password_manager=password_manager)


async def verify_trusted_ip(request: Request):
    if request.client.host not in settings.TRUSTED_IPS:
        raise AuthorizationError('Access denied from untrusted IP.')
