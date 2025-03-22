from fastapi import FastAPI
from app.apirouter import api_router
from app.core.config import config


def create_app():
    app = FastAPI(
        title=config.app_name,
        description=config.description,
        version=config.version,
        docs_url=None if not config.debug else "/docs",
        redoc_url=None if not config.debug else "/redoc",
    )
    app.include_router(api_router, prefix="/api")
    return app


app = create_app()
