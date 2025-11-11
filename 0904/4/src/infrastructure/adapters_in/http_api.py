from fastapi import APIRouter

from src.infrastructure.adapters_in import admin, answer, question, todo

api_router = APIRouter()
api_router.include_router(todo.router)
api_router.include_router(question.router)
api_router.include_router(answer.router)
api_router.include_router(admin.router)
