import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from src.infrastructure.adapters_in.http_api import api_router
from src.infrastructure.core.exception_handlers import add_exception_handlers

app = FastAPI()

add_exception_handlers(app)
app.include_router(api_router, prefix='/api/v1')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'src', 'static')
app.mount('/', StaticFiles(directory=STATIC_DIR, html=True), name='static')
