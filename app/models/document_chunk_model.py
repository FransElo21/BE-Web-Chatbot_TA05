from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
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
        )
    )

    chunk_text=Column(
        Text
    )

    chunk_index=Column(
        Integer
    )

    created_at=Column(
        DateTime,
        server_default=func.now()
    )
