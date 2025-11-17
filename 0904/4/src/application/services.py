from src.application.dtos import (
    AdminDeletedItemsResponse,
    AnswerCreateRequest,
    AnswerUpdateRequest,
    AnswerViewResponse,
    AuthRequest,
    PaginatedResponse,
    QuestionCreateRequest,
    QuestionUpdateRequest,
    QuestionViewResponse,
    TodoCreateRequest,
    TodoUpdateRequest,
    TodoViewResponse,
)
from src.application.ports import PasswordManager
from src.domain.entity import Answer, Question, Todo
from src.domain.exceptions import (
    AuthorizationError,
    EmptyTaskError,
    NotFoundError,
    ValidationError,
)
from src.domain.repos import (
    AnswerRepository,
    QuestionRepository,
    TodoRepository,
    UnitOfWork,
)


class BaseService:
    def __init__(self, *, password_manager: PasswordManager):
        self.password_manager = password_manager

    def _check_permission(
        self,
        *,
        password_hash: str,
        password: str | None = None,
    ) -> None:
        if not password:
            raise AuthorizationError('Password is required.')
        if not self.password_manager.verify(password, password_hash):
            raise AuthorizationError('Invalid password.')
        return


class TodoService(BaseService):
    def __init__(self, *, todo_repo: TodoRepository, password_manager: PasswordManager):
        self.todo_repo = todo_repo
        super().__init__(password_manager=password_manager)

    async def create_todo(
        self, *, todo_dto: TodoCreateRequest, creator_ip: str
    ) -> TodoViewResponse:
        if not todo_dto.task:
            raise EmptyTaskError('Task cannot be empty.')

        hashed_pw = self.password_manager.hash(todo_dto.password)
        new_todo = Todo(
            task=todo_dto.task,
            due_date=todo_dto.due_date,
            creator_ip=creator_ip,
            password_hash=hashed_pw,
        )
        created_todo = await self.todo_repo.add(new_todo)
        return TodoViewResponse.model_validate(created_todo)

    async def get_todos(
        self, *, skip: int = 0, limit: int = 10
    ) -> PaginatedResponse[TodoViewResponse]:
        todos, total = await self.todo_repo.get_list(skip=skip, limit=limit)
        return PaginatedResponse(
            total_items=total,
            items=[TodoViewResponse.model_validate(t) for t in todos],
            page=(skip // limit) + 1,
            page_size=limit,
        )

    async def get_todo(self, *, todo_id: str) -> TodoViewResponse:
        todo = await self.todo_repo.get(todo_id)
        if todo is None:
            raise NotFoundError(f'Todo with id {todo_id} not found.')
        return TodoViewResponse.model_validate(todo)

    async def update_todo(
        self, *, todo_id: str, todo_dto: TodoUpdateRequest
    ) -> TodoViewResponse:
        todo = await self.todo_repo.get(todo_id)
        if todo is None:
            raise NotFoundError(f'Todo with id {todo_id} not found.')
        self._check_permission(
            password_hash=todo.password_hash, password=todo_dto.password
        )

        todo.update(task=todo_dto.task, due_date=todo_dto.due_date)
        updated_todo = await self.todo_repo.update(todo)
        return TodoViewResponse.model_validate(updated_todo)

    async def complete_todo(
        self, *, todo_id: str, auth: AuthRequest
    ) -> TodoViewResponse:
        todo = await self.todo_repo.get(todo_id)
        if todo is None:
            raise NotFoundError(f'Todo with id {todo_id} not found.')
        self._check_permission(password_hash=todo.password_hash, password=auth.password)

        todo.complete()
        updated_todo = await self.todo_repo.update(todo)
        return TodoViewResponse.model_validate(updated_todo)

    async def uncomplete_todo(
        self, *, todo_id: str, auth: AuthRequest
    ) -> TodoViewResponse:
        todo = await self.todo_repo.get(todo_id)
        if todo is None:
            raise NotFoundError(f'Todo with id {todo_id} not found.')
        self._check_permission(password_hash=todo.password_hash, password=auth.password)

        todo.uncomplete()
        updated_todo = await self.todo_repo.update(todo)
        return TodoViewResponse.model_validate(updated_todo)

    async def delete_todo(self, *, todo_id: str, auth: AuthRequest) -> None:
        todo = await self.todo_repo.get(todo_id)
        if todo is None:
            raise NotFoundError(f'Todo with id {todo_id} not found.')
        self._check_permission(password_hash=todo.password_hash, password=auth.password)

        await self.todo_repo.delete(todo_id)


class QuestionService(BaseService):
    def __init__(
        self, *, question_repo: QuestionRepository, password_manager: PasswordManager
    ):
        self.question_repo = question_repo
        super().__init__(password_manager=password_manager)

    async def create_question(
        self, *, question_dto: QuestionCreateRequest, creator_ip: str
    ) -> QuestionViewResponse:
        hashed_pw = self.password_manager.hash(question_dto.password)
        new_question = Question(
            subject=question_dto.subject,
            content=question_dto.content,
            creator_ip=creator_ip,
            password_hash=hashed_pw,
        )
        created_question = await self.question_repo.add(new_question)
        return QuestionViewResponse.model_validate(created_question)

    async def get_questions(
        self, *, skip: int = 0, limit: int = 10
    ) -> PaginatedResponse[QuestionViewResponse]:
        questions, total = await self.question_repo.get_list(skip=skip, limit=limit)
        return PaginatedResponse(
            total_items=total,
            items=[QuestionViewResponse.model_validate(q) for q in questions],
            page=(skip // limit) + 1,
            page_size=limit,
        )

    async def get_question(self, *, question_id: str) -> QuestionViewResponse:
        question = await self.question_repo.get(question_id)
        if question is None:
            raise NotFoundError(f'Question with id {question_id} not found.')
        return QuestionViewResponse.model_validate(question)

    async def update_question(
        self, *, question_id: str, question_dto: QuestionUpdateRequest
    ) -> QuestionViewResponse:
        question = await self.question_repo.get(question_id)
        if question is None:
            raise NotFoundError(f'Question with id {question_id} not found.')
        self._check_permission(
            password_hash=question.password_hash, password=question_dto.password
        )

        question.update(subject=question_dto.subject, content=question_dto.content)
        return QuestionViewResponse.model_validate(
            await self.question_repo.update(question)
        )

    async def delete_question(self, *, question_id: str, auth: AuthRequest) -> None:
        question = await self.question_repo.get(question_id)
        if question is None:
            raise NotFoundError(f'Question with id {question_id} not found.')
        self._check_permission(
            password_hash=question.password_hash, password=auth.password
        )

        await self.question_repo.delete(question_id)


class AnswerService(BaseService):
    def __init__(
        self,
        *,
        answer_repo: AnswerRepository,
        question_repo: QuestionRepository,
        password_manager: PasswordManager,
    ):
        self.answer_repo = answer_repo
        self.question_repo = question_repo
        super().__init__(password_manager=password_manager)

    async def create_answer(
        self, *, answer_dto: AnswerCreateRequest, creator_ip: str
    ) -> AnswerViewResponse:
        question = await self.question_repo.get(answer_dto.question_id)
        if question is None:
            raise NotFoundError(f'Question with id {answer_dto.question_id} not found.')

        if answer_dto.parent_id:
            parent_answer = await self.answer_repo.get(answer_dto.parent_id)
            if parent_answer is None:
                raise NotFoundError(
                    f'Parent answer with id {answer_dto.parent_id} not found.'
                )
            if parent_answer.question_id != answer_dto.question_id:
                raise ValidationError(
                    'Parent answer does not belong to the same question.'
                )

        hashed_pw = self.password_manager.hash(answer_dto.password)
        new_answer = Answer(
            content=answer_dto.content,
            question_id=answer_dto.question_id,
            creator_ip=creator_ip,
            parent_id=answer_dto.parent_id,
            password_hash=hashed_pw,
        )
        created_answer = await self.answer_repo.add(new_answer)
        return AnswerViewResponse.model_validate(created_answer)

    async def get_answer(self, *, answer_id: str) -> AnswerViewResponse:
        answer = await self.answer_repo.get_any(answer_id)
        if answer is None:
            raise NotFoundError(f'Answer with id {answer_id} not found.')
        return AnswerViewResponse.model_validate(answer)

    async def update_answer(
        self, *, answer_id: str, answer_dto: AnswerUpdateRequest
    ) -> AnswerViewResponse:
        answer = await self.answer_repo.get(answer_id)
        if answer is None:
            raise NotFoundError(f'Answer with id {answer_id} not found.')
        self._check_permission(
            password_hash=answer.password_hash, password=answer_dto.password
        )

        answer.update(content=answer_dto.content)
        updated_answer = await self.answer_repo.update(answer)
        return AnswerViewResponse.model_validate(updated_answer)

    async def delete_answer(self, *, answer_id: str, auth: AuthRequest) -> None:
        answer = await self.answer_repo.get(answer_id)
        if answer is None:
            raise NotFoundError(f'Answer with id {answer_id} not found.')
        self._check_permission(
            password_hash=answer.password_hash, password=auth.password
        )

        await self.answer_repo.delete(answer_id)


class AdminService:
    def __init__(self, *, uow: UnitOfWork):
        self.uow = uow

    async def get_deleted_items(
        self, *, skip: int, limit: int
    ) -> AdminDeletedItemsResponse:
        page = (skip // limit) + 1

        deleted_todos, total_todos = await self.uow.todo_repo.get_deleted_list(
            skip=skip, limit=limit
        )
        (
            deleted_questions,
            total_questions,
        ) = await self.uow.question_repo.get_deleted_list(skip=skip, limit=limit)
        deleted_answers, total_answers = await self.uow.answer_repo.get_deleted_list(
            skip=skip, limit=limit
        )

        return AdminDeletedItemsResponse(
            todos=PaginatedResponse(
                total_items=total_todos,
                items=[TodoViewResponse.model_validate(t) for t in deleted_todos],
                page=page,
                page_size=limit,
            ),
            questions=PaginatedResponse(
                total_items=total_questions,
                items=[
                    QuestionViewResponse.model_validate(q) for q in deleted_questions
                ],
                page=page,
                page_size=limit,
            ),
            answers=PaginatedResponse(
                total_items=total_answers,
                items=[AnswerViewResponse.model_validate(a) for a in deleted_answers],
                page=page,
                page_size=limit,
            ),
        )

    async def soft_delete_item(self, *, item_type: str, item_id: str) -> None:
        repo = None
        if item_type == 'todos':
            repo = self.uow.todo_repo
        elif item_type == 'questions':
            repo = self.uow.question_repo
        elif item_type == 'answers':
            repo = self.uow.answer_repo
        else:
            raise NotFoundError(f'Invalid item type: {item_type}')

        item = await repo.get(item_id)
        if item is None:
            raise NotFoundError(f'{item_type} with id {item_id} not found.')

        await repo.delete(item_id)

    async def hard_delete_item(self, *, item_type: str, item_id: str) -> None:
        repo = None
        if item_type == 'todos':
            repo = self.uow.todo_repo
        elif item_type == 'questions':
            repo = self.uow.question_repo
        elif item_type == 'answers':
            repo = self.uow.answer_repo
        else:
            raise NotFoundError(f'Invalid item type: {item_type}')

        item = await repo.get_any(item_id)
        if item is None:
            raise NotFoundError(f'{item_type} with id {item_id} not found.')

        await repo.hard_delete(item_id)
