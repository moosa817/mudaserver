from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterInput(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=20,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Username must be 3-20 characters long and can only contain letters, numbers, and underscores.",
    )
    email: EmailStr  # Ensures a valid email format
    password: str = Field(
        ...,
        min_length=8,
        max_length=50,
        description="Password must be 8-50 characters long.",
    )
    confirm_password: str = Field(
        ..., min_length=8, max_length=50, description="Must match the password."
    )

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, confirm_password, values):
        if confirm_password != values.data["password"]:
            raise ValueError("Passwords do not match")
        return confirm_password
