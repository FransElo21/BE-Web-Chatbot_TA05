from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.sql import func

from app.database import Base


class ChatMessage(Base):

    __tablename__="chat_messages"

    id_message=Column(
        Integer,
        primary_key=True
    )

    id_session=Column(
        Integer,
        ForeignKey(
            "chat_sessions.id_session"
        )
    )

    sender=Column(
        String
    )

    message_text=Column(
        Text
    )

    created_at=Column(
        DateTime,
        server_default=func.now()
    )