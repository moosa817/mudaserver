from pydantic import BaseModel, EmailStr, Field


class UpdateUserRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username must be 3-20 characters long and can only contain letters, numbers, and underscores.",
    )
    email: EmailStr  # Ensures a valid email format
