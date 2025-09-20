from fastapi import FastAPI, Request
from app.apirouter import api_router
from app.core.config import config
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware


def create_app():

    cors_origins = ["http://localhost:3000", "https://myfrontend.com", "*"]

    app = FastAPI(
        title=config.app_name,
        description=config.description,
        version=config.version,
        docs_url=None if not config.debug else "/docs",
        redoc_url=None if not config.debug else "/redoc",
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
