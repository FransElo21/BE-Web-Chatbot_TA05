from fastapi import Depends
from fastapi import HTTPException
from fastapi import Cookie
from fastapi import status

from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.auth_service import verify_token


def get_current_user(

    access_token: str | None =
    Cookie(default=None),

    db: Session =
    Depends(get_db)

):

    if not access_token:

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )

    user = verify_token(
        db=db,
        token=access_token
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return user


def require_admin(

    user = Depends(get_current_user)

):

    if user.role != "admin":

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    return user
