from pydantic import BaseModel


class RegisterResponse(BaseModel):
    id: int
    username: str
    email: str
    pfp: str
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
