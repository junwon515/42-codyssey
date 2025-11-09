from fastapi import APIRouter, Depends, status

from src.application.services import TodoService
from src.infrastructure.adapters_in.dtos import (
    TodoCreateRequest,
    TodoItem,
    TodoViewResponse,
)
from src.infrastructure.core.dependencies import get_todo_service

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


@router.get('/{todo_id}', response_model=TodoViewResponse)
def get_single_todo(
    todo_id: str, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    todo_entity = service.get_todo(todo_id=todo_id)
    return TodoViewResponse.model_validate(todo_entity)


@router.put('/{todo_id}', response_model=TodoViewResponse)
def update_todo(
    todo_id: str, todo_dto: TodoItem, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    updated_todo_entity = service.update_todo(
        todo_id=todo_id,
        task=todo_dto.task,
        due_date=todo_dto.due_date,
    )
    return TodoViewResponse.model_validate(updated_todo_entity)


@router.delete('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_single_todo(
    todo_id: str, service: TodoService = Depends(get_todo_service)
) -> None:
    service.delete_todo(todo_id=todo_id)
