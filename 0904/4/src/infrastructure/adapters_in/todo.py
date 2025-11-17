from fastapi import APIRouter, Depends, Query, Request, status

from src.application.dtos import (
    AuthRequest,
    PaginatedResponse,
    TodoCreateRequest,
    TodoUpdateRequest,
    TodoViewResponse,
)
from src.application.services import TodoService
from src.infrastructure.core.dependencies import get_todo_service

router = APIRouter(prefix='/todo', tags=['todo'])


@router.post('/', response_model=TodoViewResponse, status_code=status.HTTP_201_CREATED)
async def add_todo(
    todo_dto: TodoCreateRequest,
    request: Request,
    service: TodoService = Depends(get_todo_service),
) -> TodoViewResponse:
    return await service.create_todo(todo_dto=todo_dto, creator_ip=request.client.host)


@router.get('/', response_model=PaginatedResponse[TodoViewResponse])
async def get_todos(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: TodoService = Depends(get_todo_service),
) -> PaginatedResponse[TodoViewResponse]:
    return await service.get_todos(skip=skip, limit=limit)


@router.get('/{todo_id}', response_model=TodoViewResponse)
async def get_single_todo(
    todo_id: str, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    return await service.get_todo(todo_id=todo_id)


@router.put('/{todo_id}', response_model=TodoViewResponse)
async def update_todo(
    todo_id: str,
    todo_dto: TodoUpdateRequest,
    service: TodoService = Depends(get_todo_service),
) -> TodoViewResponse:
    return await service.update_todo(todo_id=todo_id, todo_dto=todo_dto)


@router.post('/{todo_id}/complete', response_model=TodoViewResponse)
async def mark_todo_as_complete(
    todo_id: str, auth: AuthRequest, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    return await service.complete_todo(todo_id=todo_id, auth=auth)


@router.post('/{todo_id}/uncomplete', response_model=TodoViewResponse)
async def mark_todo_as_uncomplete(
    todo_id: str, auth: AuthRequest, service: TodoService = Depends(get_todo_service)
) -> TodoViewResponse:
    return await service.uncomplete_todo(todo_id=todo_id, auth=auth)


@router.delete('/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_todo(
    todo_id: str, auth: AuthRequest, service: TodoService = Depends(get_todo_service)
) -> None:
    await service.delete_todo(todo_id=todo_id, auth=auth)
