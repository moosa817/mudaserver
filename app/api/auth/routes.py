from fastapi import APIRouter
from app.api.auth.token import tokenroute
from app.api.auth.refresh import refreshroute
from app.api.auth.register import registerroute
from app.api.auth.update_user import updateroute

authrouter = APIRouter()

authrouter.include_router(registerroute)
authrouter.include_router(tokenroute)
authrouter.include_router(refreshroute)
authrouter.include_router(updateroute)
