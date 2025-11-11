import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from src.domain.exceptions import (
    AuthorizationError,
    EmptyTaskError,
    NotFoundError,
    PersistenceError,
    ValidationError,
)

log = logging.getLogger(__name__)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(EmptyTaskError)
    async def empty_task_exception_handler(request: Request, exc: EmptyTaskError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST, content={'warning': exc.message}
        )

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND, content={'warning': exc.message}
        )

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={'warning': exc.message},
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(
        request: Request, exc: AuthorizationError
    ):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN, content={'error': exc.message}
        )

    @app.exception_handler(PersistenceError)
    async def persistence_exception_handler(request: Request, exc: PersistenceError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'error': 'An internal error occurred while processing data.'},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        log.critical(f'Unhandled exception occurred: {exc}', exc_info=True)

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={'error': 'An unexpected internal server error occurred.'},
        )
