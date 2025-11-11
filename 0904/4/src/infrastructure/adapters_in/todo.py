from fastapi import APIRouter, Depends, Query, Request, status

from src.application.services import TodoService
from src.infrastructure.adapters_in.dtos import (
    AuthRequest,
    PaginatedResponse,
    TodoCreateRequest,
    TodoUpdateRequest,
    TodoViewResponse,
)
from src.infrastructure.core.dependencies import get_todo_service

router = APIRouter(prefix='/todo', tags=['todo'])


@router.post('/', response_model=TodoViewResponse, status_code=status.HTTP_201_CREATED)
async def add_todo(
    todo_dto: TodoCreateRequest,
    request: Request,
    service: TodoService = Depends(get_todo_service),
) -> TodoViewResponse:
    new_todo_entity = await service.create_todo(
        task=todo_dto.task,
        due_date=todo_dto.due_date,
        creator_ip=request.client.host,
        password=todo_dto.password,
    )
    return TodoViewResponse.model_validate(new_todo_entity)


@router.get('/', response_model=PaginatedResponse[TodoViewResponse])
async def get_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: TodoService = Depends(get_todo_service),
) -> PaginatedResponse[TodoViewResponse]:
    items, total = await service.get_todos(skip=skip, limit=limit)
    return PaginatedResponse(
        total_items=total,
        items=[TodoViewResponse.model_validate(e) for e in items],
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get('/{todo_id}', response_model=TodoViewResponse)
async def get_single_todo(
    todo_id: str, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    todo_entity = await service.get_todo(todo_id=todo_id)
    return TodoViewResponse.model_validate(todo_entity)


@router.put('/{todo_id}', response_model=TodoViewResponse)
async def update_todo(
    todo_id: str,
    todo_dto: TodoUpdateRequest,
    service: TodoService = Depends(get_todo_service),
) -> TodoViewResponse:
    updated_todo_entity = await service.update_todo(
        todo_id=todo_id,
        task=todo_dto.task,
        due_date=todo_dto.due_date,
        password=todo_dto.password,
    )
    return TodoViewResponse.model_validate(updated_todo_entity)


@router.post('/{todo_id}/complete', response_model=TodoViewResponse)
async def mark_todo_as_complete(
    todo_id: str, auth: AuthRequest, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    updated_todo = await service.complete_todo(
        todo_id=todo_id,
        password=auth.password,
    )
    return TodoViewResponse.model_validate(updated_todo)


@router.post('/{todo_id}/uncomplete', response_model=TodoViewResponse)
async def mark_todo_as_uncomplete(
    todo_id: str, auth: AuthRequest, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    updated_todo = await service.uncomplete_todo(
        todo_id=todo_id,
        password=auth.password,
    )
    return TodoViewResponse.model_validate(updated_todo)


@router.delete('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_todo(
    todo_id: str, auth: AuthRequest, service: TodoService = Depends(get_todo_service)
) -> None:
    await service.delete_todo(
        todo_id=todo_id,
        password=auth.password,
    )
