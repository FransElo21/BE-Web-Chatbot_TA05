from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy import TIMESTAMP
from sqlalchemy.sql import func

from app.database import Base


class DocumentChunk(Base):

    __tablename__="document_chunks"
    id_chunk=Column(
        Integer,
        primary_key=True
    )

    id_document=Column(

        Integer,
        ForeignKey(
            "documents.id_document"
        ),
        nullable=False
    )

    content=Column(
        Text,
        nullable=False
    )

    chunk_index=Column(
        Integer,
        nullable=False
    )

    created_at=Column(
        TIMESTAMP,
        server_default=func.now()
    )

    bab=Column(
        Text,
        nullable=True
    )

    pasal=Column(
        Text,
        nullable=True
    )

    ayat=Column(
        Integer,
        nullable=True
    )

    halaman=Column(
        Integer,
        nullable=True
    )
