from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.database import Base


class ChatSession(Base):

    __tablename__="chat_sessions"

    id_session=Column(
        Integer,
        primary_key=True
    )

    id_user=Column(
        Integer,
        ForeignKey(
            "users.id_user"
        )
    )

    session_title=Column(
        String
    )

    created_at=Column(
        DateTime,
        server_default=func.now()
    )