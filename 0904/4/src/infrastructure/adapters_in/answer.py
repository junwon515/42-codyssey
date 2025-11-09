from fastapi import APIRouter, Depends, status

from src.application.services import AnswerService
from src.infrastructure.adapters_in.dtos import (
    AnswerCreateRequest,
    AnswerUpdateRequest,
    AnswerViewResponse,
)
from src.infrastructure.core.dependencies import get_answer_service

router = APIRouter(prefix='/answer', tags=['answer'])


@router.post(
    '/', response_model=AnswerViewResponse, status_code=status.HTTP_201_CREATED
)
async def add_answer(
    answer_dto: AnswerCreateRequest,
    service: AnswerService = Depends(get_answer_service),
) -> AnswerViewResponse:
    new_answer_entity = await service.create_answer(
        question_id=answer_dto.question_id, content=answer_dto.content
    )
    return AnswerViewResponse.model_validate(new_answer_entity)


@router.get('/{answer_id}', response_model=AnswerViewResponse)
async def get_single_answer(
    answer_id: str, service: AnswerService = Depends(get_answer_service)
) -> AnswerViewResponse:
    answer_entity = await service.get_answer(answer_id=answer_id)
    return AnswerViewResponse.model_validate(answer_entity)


@router.put('/{answer_id}', response_model=AnswerViewResponse)
async def update_answer(
    answer_id: str,
    answer_dto: AnswerUpdateRequest,
    service: AnswerService = Depends(get_answer_service),
) -> AnswerViewResponse:
    updated_answer_entity = await service.update_answer(
        answer_id=answer_id,
        content=answer_dto.content,
    )
    return AnswerViewResponse.model_validate(updated_answer_entity)


@router.delete('/{answer_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_answer(
    answer_id: str, service: AnswerService = Depends(get_answer_service)
) -> None:
    await service.delete_answer(answer_id=answer_id)
