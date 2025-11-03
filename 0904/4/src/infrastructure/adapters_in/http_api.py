from fastapi import APIRouter

from src.infrastructure.adapters_in import todo

api_router = APIRouter()
api_router.include_router(todo.router)
