from jose import jwt
from datetime import datetime,timedelta

from app.config import (
    SECRET_KEY,
    ALGORITHM
)


def create_access_token(data):

    payload=data.copy()

    expire=datetime.utcnow()+timedelta(
        minutes=60
    )

    payload.update(
        {"exp":expire}
    )

    token=jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token