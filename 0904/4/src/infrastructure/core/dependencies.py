from collections.abc import AsyncGenerator

from fastapi import Depends, Request

from src.application.services import (
    AdminService,
    AnswerService,
    QuestionService,
    TodoService,
)
from src.domain.exceptions import AuthorizationError
from src.domain.ports import (
    AnswerRepository,
    PasswordManager,
    QuestionRepository,
    TodoRepository,
    UnitOfWork,
)
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


async def get_todo_repo(uow: UnitOfWork = Depends(get_uow)) -> TodoRepository:
    return uow.todo_repo


async def get_question_repo(uow: UnitOfWork = Depends(get_uow)) -> QuestionRepository:
    return uow.question_repo


async def get_answer_repo(uow: UnitOfWork = Depends(get_uow)) -> AnswerRepository:
    return uow.answer_repo


def get_password_manager() -> PasswordManager:
    return BcryptPasswordManager()


def get_admin_service(uow: UnitOfWork = Depends(get_uow)) -> AdminService:
    return AdminService(uow=uow)


def get_todo_service(
    todo_repo: TodoRepository = Depends(get_todo_repo),
    password_manager: PasswordManager = Depends(get_password_manager),
) -> TodoService:
    return TodoService(todo_repo=todo_repo, password_manager=password_manager)


def get_question_service(
    question_repo: QuestionRepository = Depends(get_question_repo),
    password_manager: PasswordManager = Depends(get_password_manager),
) -> QuestionService:
    return QuestionService(
        question_repo=question_repo, password_manager=password_manager
    )


def get_answer_service(
    answer_repo: AnswerRepository = Depends(get_answer_repo),
    question_repo: QuestionRepository = Depends(get_question_repo),
    password_manager: PasswordManager = Depends(get_password_manager),
) -> AnswerService:
    return AnswerService(
        answer_repo=answer_repo,
        question_repo=question_repo,
        password_manager=password_manager,
    )


async def verify_trusted_ip(request: Request):
    if request.client.host not in settings.TRUSTED_IPS:
        raise AuthorizationError('Access denied from untrusted IP.')
