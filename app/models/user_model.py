from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.database import Base


class User(Base):

    __tablename__="users"

    id_user=Column(
        Integer,
        primary_key=True,
        index=True
    )

    name=Column(
        String,
        nullable=False
    )

    email=Column(
        String,
        unique=True,
        nullable=False
    )

    password=Column(
        String,
        nullable=False
    )

    role=Column(
        String,
        default="user"
    )

    created_at=Column(
        DateTime(timezone=True),
        server_default=func.now()
    )