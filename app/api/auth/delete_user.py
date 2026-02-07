from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.dependencies import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from pydantic import BaseModel, Field
from app.services.auth.security import verify_password
import logging

logger = logging.getLogger(__name__)
deleteroute = APIRouter()


class DeleteUserRequest(BaseModel):
    password: str = Field(..., min_length=8)


@deleteroute.delete("/delete_user")
async def delete_user(
    request: DeleteUserRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete user account."""
    try:
        # Verify the password
        if not verify_password(request.password, user.hashed_password):
            raise HTTPException(status_code=403, detail="Invalid password")

        # Delete the user
        db.delete(user)
        db.commit()

        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during user deletion: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="An error occurred during user deletion. Please try again.",
        )
