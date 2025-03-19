from fastapi import FastAPI
from app.apirouter import api_router
from app.core.config import config


def create_app():
    app = FastAPI()
    app.include_router(api_router, prefix="/api")
    return app

app = create_app()

