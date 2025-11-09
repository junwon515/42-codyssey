import logging

log = logging.getLogger(__name__)


class ApplicationBaseError(Exception):
    @property
    def message(self) -> str:
        return self.__str__()


class BusinessError(ApplicationBaseError):
    pass


class InfrastructureError(ApplicationBaseError):
    def __init__(self, message: str, original_exception: Exception = None):
        super().__init__(message)
        self.original_exception = original_exception

        log.error(f'{self.__class__.__name__}: {message}', exc_info=original_exception)


class EmptyTaskError(BusinessError):
    def __init__(self, message: str = 'Task cannot be empty.'):
        super().__init__(message)


class NotFoundError(BusinessError):
    def __init__(self, message: str = 'Requested resource not found.'):
        super().__init__(message)


class PersistenceError(InfrastructureError):
    def __init__(self, original_exception: Exception):
        super().__init__(
            message=f'A persistence error occurred: {original_exception}',
            original_exception=original_exception,
        )
