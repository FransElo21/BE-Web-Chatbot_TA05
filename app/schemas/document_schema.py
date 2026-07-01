from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class DocumentResponse(
    BaseModel
):
    id_document:int
    title:str
    file_name:str
    file_path:str
    uploaded_by:int
    id_category:int
    created_at:datetime

    class Config:
        from_attributes=True


class UpdateDocumentRequest(
    BaseModel
):
    title:Optional[str]=None
    id_category:Optional[int]=None