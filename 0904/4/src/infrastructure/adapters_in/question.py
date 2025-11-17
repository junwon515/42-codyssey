from fastapi import APIRouter, Depends, Query, Request, status

from src.application.dtos import (
    AuthRequest,
    PaginatedResponse,
    QuestionCreateRequest,
    QuestionUpdateRequest,
    QuestionViewResponse,
)
from src.application.services import QuestionService
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
    return await service.create_question(
        question_dto=question_dto, creator_ip=request.client.host
    )


@router.get('/', response_model=PaginatedResponse[QuestionViewResponse])
async def get_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: QuestionService = Depends(get_question_service),
) -> PaginatedResponse[QuestionViewResponse]:
    return await service.get_questions(skip=skip, limit=limit)


@router.get('/{question_id}', response_model=QuestionViewResponse)
async def get_single_question(
    question_id: str, service: QuestionService = Depends(get_question_service)
) -> QuestionViewResponse:
    return await service.get_question(question_id=question_id)


@router.put('/{question_id}', response_model=QuestionViewResponse)
async def update_question(
    question_id: str,
    question_dto: QuestionUpdateRequest,
    service: QuestionService = Depends(get_question_service),
) -> QuestionViewResponse:
    return await service.update_question(
        question_id=question_id,
        question_dto=question_dto,
    )


@router.delete('/{question_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_single_question(
    question_id: str,
    auth: AuthRequest,
    service: QuestionService = Depends(get_question_service),
) -> None:
    await service.delete_question(
        question_id=question_id,
        auth=auth,
    )
