from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Cookie
from fastapi import Response

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.auth_schema import (
    RegisterRequest,
    LoginRequest
)

from app.services.auth_service import (
    register,
    login,
    verify_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/register")
def register_user(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):

    try:

        user = register(
            db=db,
            data=data
        )

        return {

            "message": "Register success",

            "user": {

                "id":
                user.id_user,

                "name":
                user.name,

                "email":
                user.email,

                "role":
                user.role

            }

        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/login")
def login_user(
    data: LoginRequest,
    response: Response,
    db: Session = Depends(get_db)
):

    try:

        result = login(
            db=db,
            data=data
        )

        token = result["access_token"]

        response.set_cookie(

            key="access_token",
            value=token,
            httponly=True,
            secure=False,
            # True kalau production HTTPS

            samesite="lax",
            max_age=60*60*24
            # 1 hari
        )

        return {

            "message":
            "Login success",

            "access_token":
            token,

            "token_type":
            "bearer",

            "user":
            result["user"]
        }

    except Exception as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get("/me")
def get_me(

    access_token: str | None =
    Cookie(default=None),

    db: Session =
    Depends(get_db)

):

    if not access_token:

        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    user = verify_token(
        db=db,
        token=access_token
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    return {

        "id":
        user.id_user,

        "name":
        user.name,

        "email":
        user.email,

        "role":
        user.role
    }

@router.post("/logout")
def logout(
    response: Response
):
    response.delete_cookie(
        key="access_token"
    )

    return {
        "message":
        "Logout success"
    }