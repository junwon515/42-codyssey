from fastapi import APIRouter, Depends, Request, status

from src.application.dtos import (
    AnswerCreateRequest,
    AnswerUpdateRequest,
    AnswerViewResponse,
    AuthRequest,
)
from src.application.services import AnswerService
from src.infrastructure.core.dependencies import get_answer_service

router = APIRouter(prefix='/answer', tags=['answer'])


@router.post(
    '/', response_model=AnswerViewResponse, status_code=status.HTTP_201_CREATED
)
async def add_answer(
    answer_dto: AnswerCreateRequest,
    request: Request,
    service: AnswerService = Depends(get_answer_service),
) -> AnswerViewResponse:
    return await service.create_answer(
        answer_dto=answer_dto, creator_ip=request.client.host
    )


@router.get('/{answer_id}', response_model=AnswerViewResponse)
async def get_single_answer(
    answer_id: str, service: AnswerService = Depends(get_answer_service)
) -> AnswerViewResponse:
    return await service.get_answer(answer_id=answer_id)


@router.put('/{answer_id}', response_model=AnswerViewResponse)
async def update_answer(
    answer_id: str,
    answer_dto: AnswerUpdateRequest,
    service: AnswerService = Depends(get_answer_service),
) -> AnswerViewResponse:
    return await service.update_answer(
        answer_id=answer_id,
        answer_dto=answer_dto,
    )


@router.delete('/{answer_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_answer(
    answer_id: str,
    auth: AuthRequest,
    service: AnswerService = Depends(get_answer_service),
) -> None:
    await service.delete_answer(
        answer_id=answer_id,
        auth=auth,
    )
