from fastapi import APIRouter, Request

from src.infrastructure.adapters_in.dtos import AuthStatusResponse
from src.infrastructure.core.config import settings

router = APIRouter(prefix='/auth', tags=['auth'])


@router.get('/status', response_model=AuthStatusResponse)
async def get_auth_status(request: Request) -> AuthStatusResponse:
    is_admin = request.client.host in settings.TRUSTED_IPS
    return AuthStatusResponse(is_admin=is_admin)
