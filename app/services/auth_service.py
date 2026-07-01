from jose import jwt
from jose import JWTError
from app.models.user_model import User

from app.repositories.user_repository import (
    get_by_email,
    create_user
)

from app.utils.hash import (
    hash_password,
    verify_password
)

from app.utils.jwt_handler import (
    create_access_token,
    SECRET_KEY,
    ALGORITHM
)


def register(
    db,
    data
):

    existing_user = get_by_email(
        db,
        data.email
    )

    if existing_user:

        raise Exception(
            "Email already exists"
        )

    user = User(

        name=data.name,

        email=data.email,

        password=hash_password(
            data.password
        ),

        role="user"
    )

    return create_user(
        db,
        user
    )


def login(
    db,
    data
):

    user = get_by_email(
        db,
        data.email
    )

    if not user:

        raise Exception(
            "User not found"
        )

    valid = verify_password(

        data.password,

        user.password

    )

    if not valid:

        raise Exception(
            "Wrong password"
        )

    token = create_access_token(

        {

            "id_user":
            user.id_user,

            "email":
            user.email,

            "role":
            user.role

        }

    )

    return {
        "access_token":token,
        "user":{
            "id_user":user.id_user,
            "name":user.name,
            "email":user.email,
            "role":user.role
        }
    }


def verify_token(
    db,
    token:str
):

    try:

        payload = jwt.decode(

            token,

            SECRET_KEY,

            algorithms=[
                ALGORITHM
            ]

        )

        user_id = payload.get(
            "id_user"
        )

        if not user_id:

            return None

        user = (

            db.query(User)

            .filter(
                User.id_user ==
                user_id
            )

            .first()

        )

        return user

    except JWTError:

        return None