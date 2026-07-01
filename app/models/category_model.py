from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class Category(Base):
    __tablename__="categories"

    id_category=Column(
        Integer,
        primary_key=True,
        index=True
    )

    name=Column(
        String,
        nullable=False,
        unique=True
    )

    description=Column(
        Text,
        nullable=True
    )

    created_at=Column(
        DateTime,
        server_default=func.now()
    )

    documents=relationship(
        "Document",
        back_populates="category"
    )