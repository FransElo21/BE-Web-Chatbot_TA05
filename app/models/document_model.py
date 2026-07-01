from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import ForeignKey
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Document(Base):

    __tablename__="documents"
    id_document=Column(
        Integer,
        primary_key=True
    )

    title=Column(
        String
    )

    file_name=Column(
        String
    )

    file_path=Column(
        String
    )

    uploaded_by=Column(
        Integer
    )

    id_category=Column(

        Integer,
        ForeignKey(
            "categories.id_category"
        )
    )

    created_at=Column(
        DateTime,
        server_default=func.now()
    )

    category=relationship(
        "Category",
        back_populates="documents"
    )