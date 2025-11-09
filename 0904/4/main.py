from fastapi import FastAPI
from src.infrastructure.adapters_in.http_api import api_router
from src.infrastructure.core.exception_handlers import add_exception_handlers

app = FastAPI()

add_exception_handlers(app)
app.include_router(api_router, prefix='/api/v1')
