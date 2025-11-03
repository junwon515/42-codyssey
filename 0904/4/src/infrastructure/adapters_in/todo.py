from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict

from src.application.services import TodoService
from src.infrastructure.core.dependencies import get_todo_service


class TodoCreateRequest(BaseModel):
    task: str | None = None
    due_date: str | None = None


class TodoViewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task: str
    due_date: str | None = None
    is_completed: bool


router = APIRouter(prefix='/todo', tags=['todo'])


@router.post('/', response_model=TodoViewResponse, status_code=status.HTTP_201_CREATED)
def add_todo(
    todo_dto: TodoCreateRequest, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    new_todo_entity = service.create_todo(
        task=todo_dto.task, due_date=todo_dto.due_date
    )
    return TodoViewResponse.model_validate(new_todo_entity)


@router.get('/', response_model=list[TodoViewResponse])
def retrieve_todo(
    service: TodoService = Depends(get_todo_service),
) -> list[TodoViewResponse]:
    todo_entities = service.get_all_todos()
    return [TodoViewResponse.model_validate(entity) for entity in todo_entities]
