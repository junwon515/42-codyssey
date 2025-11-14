from datetime import date

from src.domain.exceptions import (
    AuthorizationError,
    EmptyTaskError,
    NotFoundError,
    ValidationError,
)
from src.domain.models import Answer, Question, Todo
from src.domain.ports import (
    AnswerRepository,
    PasswordManager,
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
        self, *, task: str | None, due_date: date | None, creator_ip: str, password: str
    ) -> Todo:
        if not task:
            raise EmptyTaskError('Task cannot be empty.')

        hashed_pw = self.password_manager.hash(password)
        new_todo = Todo(
            task=task,
            due_date=due_date,
            creator_ip=creator_ip,
            password_hash=hashed_pw,
        )
        return await self.todo_repo.add(new_todo)

    async def get_todos(
        self, *, skip: int = 0, limit: int = 10
    ) -> tuple[list[Todo], int]:
        return await self.todo_repo.get_list(skip=skip, limit=limit)

    async def get_todo(self, *, todo_id: str) -> Todo:
        todo = await self.todo_repo.get(todo_id)
        if todo is None:
            raise NotFoundError(f'Todo with id {todo_id} not found.')
        return todo

    async def update_todo(
        self, *, todo_id: str, task: str, due_date: date | None, password: str
    ) -> Todo:
        todo = await self.get_todo(todo_id=todo_id)
        self._check_permission(password_hash=todo.password_hash, password=password)

        todo.update(task=task, due_date=due_date)
        return await self.todo_repo.update(todo)

    async def complete_todo(self, *, todo_id: str, password: str) -> Todo:
        todo = await self.get_todo(todo_id=todo_id)
        self._check_permission(password_hash=todo.password_hash, password=password)

        todo.complete()
        return await self.todo_repo.update(todo)

    async def uncomplete_todo(self, *, todo_id: str, password: str) -> Todo:
        todo = await self.get_todo(todo_id=todo_id)
        self._check_permission(password_hash=todo.password_hash, password=password)

        todo.uncomplete()
        return await self.todo_repo.update(todo)

    async def delete_todo(self, *, todo_id: str, password: str) -> None:
        todo = await self.get_todo(todo_id=todo_id)
        self._check_permission(password_hash=todo.password_hash, password=password)

        await self.todo_repo.delete(todo_id)


class QuestionService(BaseService):
    def __init__(
        self, *, question_repo: QuestionRepository, password_manager: PasswordManager
    ):
        self.question_repo = question_repo
        super().__init__(password_manager=password_manager)

    async def create_question(
        self, *, subject: str, content: str, creator_ip: str, password: str
    ) -> Question:
        hashed_pw = self.password_manager.hash(password)
        new_question = Question(
            subject=subject,
            content=content,
            creator_ip=creator_ip,
            password_hash=hashed_pw,
        )
        return await self.question_repo.add(new_question)

    async def get_questions(
        self, *, skip: int = 0, limit: int = 10
    ) -> tuple[list[Question], int]:
        return await self.question_repo.get_list(skip=skip, limit=limit)

    async def get_question(self, *, question_id: str) -> Question:
        question = await self.question_repo.get(question_id)
        if question is None:
            raise NotFoundError(f'Question with id {question_id} not found.')
        return question

    async def update_question(
        self, *, question_id: str, subject: str, content: str, password: str
    ) -> Question:
        question = await self.get_question(question_id=question_id)
        self._check_permission(password_hash=question.password_hash, password=password)

        question.update(subject=subject, content=content)
        return await self.question_repo.update(question)

    async def delete_question(self, *, question_id: str, password: str) -> None:
        question = await self.get_question(question_id=question_id)
        self._check_permission(password_hash=question.password_hash, password=password)

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
        self,
        *,
        question_id: str,
        content: str,
        creator_ip: str,
        password: str,
        parent_id: str | None = None,
    ) -> Answer:
        question = await self.question_repo.get(question_id)
        if question is None:
            raise NotFoundError(f'Question with id {question_id} not found.')

        if parent_id:
            parent_answer = await self.answer_repo.get(parent_id)
            if parent_answer is None:
                raise NotFoundError(f'Parent answer with id {parent_id} not found.')
            if parent_answer.question_id != question_id:
                raise ValidationError(
                    'Parent answer does not belong to the same question.'
                )

        hashed_pw = self.password_manager.hash(password)
        new_answer = Answer(
            content=content,
            question_id=question_id,
            creator_ip=creator_ip,
            parent_id=parent_id,
            password_hash=hashed_pw,
        )
        return await self.answer_repo.add(new_answer)

    async def get_answer(self, *, answer_id: str) -> Answer:
        answer = await self.answer_repo.get_any(answer_id)
        if answer is None:
            raise NotFoundError(f'Answer with id {answer_id} not found.')
        return answer

    async def update_answer(
        self, *, answer_id: str, content: str, password: str
    ) -> Answer:
        answer = await self.answer_repo.get(answer_id)
        if answer is None:
            raise NotFoundError(f'Answer with id {answer_id} not found.')
        self._check_permission(password_hash=answer.password_hash, password=password)

        answer.update(content=content)
        return await self.answer_repo.update(answer)

    async def delete_answer(self, *, answer_id: str, password: str) -> None:
        answer = await self.answer_repo.get(answer_id)
        if answer is None:
            raise NotFoundError(f'Answer with id {answer_id} not found.')
        self._check_permission(password_hash=answer.password_hash, password=password)

        await self.answer_repo.delete(answer_id)


class AdminService:
    def __init__(self, *, uow: UnitOfWork):
        self.uow = uow

    async def get_deleted_items(self, *, skip: int, limit: int) -> dict:
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

        return {
            'todos': {
                'total_items': total_todos,
                'items': deleted_todos,
                'page': page,
                'page_size': limit,
            },
            'questions': {
                'total_items': total_questions,
                'items': deleted_questions,
                'page': page,
                'page_size': limit,
            },
            'answers': {
                'total_items': total_answers,
                'items': deleted_answers,
                'page': page,
                'page_size': limit,
            },
        }

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
