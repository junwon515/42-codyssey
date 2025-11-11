from fastapi import APIRouter, Depends, Query, Request, status

from src.application.services import QuestionService
from src.infrastructure.adapters_in.dtos import (
    AuthRequest,
    PaginatedResponse,
    QuestionCreateRequest,
    QuestionUpdateRequest,
    QuestionViewResponse,
)
from src.infrastructure.core.dependencies import get_question_service

router = APIRouter(prefix='/question', tags=['question'])


@router.post(
    '/', response_model=QuestionViewResponse, status_code=status.HTTP_201_CREATED
)
async def add_question(
    question_dto: QuestionCreateRequest,
    request: Request,
    service: QuestionService = Depends(get_question_service),
) -> QuestionViewResponse:
    new_question_entity = await service.create_question(
        subject=question_dto.subject,
        content=question_dto.content,
        creator_ip=request.client.host,
        password=question_dto.password,
    )
    return QuestionViewResponse.model_validate(new_question_entity)


@router.get('/', response_model=PaginatedResponse[QuestionViewResponse])
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: QuestionService = Depends(get_question_service),
) -> PaginatedResponse[QuestionViewResponse]:
    items, total = await service.get_questions(skip=skip, limit=limit)
    return PaginatedResponse(
        total_items=total,
        items=[QuestionViewResponse.model_validate(e) for e in items],
        page=(skip // limit) + 1,
        page_size=limit,
    )


@router.get('/{question_id}', response_model=QuestionViewResponse)
async def get_single_question(
    question_id: str, service: QuestionService = Depends(get_question_service)
) -> QuestionViewResponse:
    question_entity = await service.get_question(question_id=question_id)
    return QuestionViewResponse.model_validate(question_entity)


@router.put('/{question_id}', response_model=QuestionViewResponse)
async def update_question(
    question_id: str,
    question_dto: QuestionUpdateRequest,
    service: QuestionService = Depends(get_question_service),
) -> QuestionViewResponse:
    updated_question_entity = await service.update_question(
        question_id=question_id,
        subject=question_dto.subject,
        content=question_dto.content,
        password=question_dto.password,
    )
    return QuestionViewResponse.model_validate(updated_question_entity)


@router.delete('/{question_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_question(
    question_id: str,
    auth: AuthRequest,
    service: QuestionService = Depends(get_question_service),
) -> None:
    await service.delete_question(
        question_id=question_id,
        password=auth.password,
    )
