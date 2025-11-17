from fastapi import APIRouter, Depends, Query, status

from src.application.dtos import AdminDeletedItemsResponse
from src.application.services import AdminService
from src.infrastructure.core.dependencies import get_admin_service, verify_trusted_ip

router = APIRouter(
    prefix='/admin', tags=['admin'], dependencies=[Depends(verify_trusted_ip)]
)


@router.get('/deleted-items', response_model=AdminDeletedItemsResponse)
async def get_list_deleted_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    admin_service: AdminService = Depends(get_admin_service),
) -> AdminDeletedItemsResponse:
    return await admin_service.get_deleted_items(skip=skip, limit=limit)


@router.delete(
    '/soft-delete/{item_type}/{item_id}', status_code=status.HTTP_204_NO_CONTENT
)
async def soft_delete_item(
    item_type: str,
    item_id: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    await admin_service.soft_delete_item(
        item_type=item_type,
        item_id=item_id,
    )


@router.delete(
    '/hard-delete/{item_type}/{item_id}', status_code=status.HTTP_204_NO_CONTENT
)
async def hard_delete_item(
    item_type: str,
    item_id: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    await admin_service.hard_delete_item(
        item_type=item_type,
        item_id=item_id,
    )
