from fastapi import FastAPI, Request
from app.apirouter import api_router  # ✅ Correct import
from app.core.config import config
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.services.cleanup.scheduler import (
    start_cleanup_scheduler,
    stop_cleanup_scheduler,
)  # ✅ Add
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ✅ Use lifespan instead of deprecated @app.on_event
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown")
    """
    # Startup
    logger.info("Starting MudaServer...")
    start_cleanup_scheduler()
    logger.info("Cleanup scheduler started - runs every 6 hours")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down MudaServer...")
    stop_cleanup_scheduler()
    logger.info("Cleanup scheduler stopped")


def create_app():
    cors_origins = ["http://localhost:3000", "https://myfrontend.com", "*"]

    app = FastAPI(
        title=config.app_name,
        description=config.description,
        version=config.version,
        docs_url=None if not config.debug else "/docs",
        redoc_url=None if not config.debug else "/redoc",
        lifespan=lifespan,  # ✅ Add lifespan
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api")

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ):
        # extract first error (you can loop for more detailed handling)
        first_error = exc.errors()[0]
        field = first_error.get("loc", ["?"])[-1]
        message = first_error.get("msg", "Invalid input")

        return JSONResponse(
            status_code=422,
            content=jsonable_encoder(
                {
                    "success": False,
                    "field": field,
                    "message": message,
                }
            ),
        )

    return app


app = create_app()
