from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class CategoryResponse(
    BaseModel
):
    id_category:int
    name:str
    description:Optional[str]=None
    created_at:datetime

    class Config:
        from_attributes=True


class CreateCategoryRequest(
    BaseModel
):
    name:str
    description:Optional[str]=None


class UpdateCategoryRequest(
    BaseModel
):
    name:Optional[str]=None
    description:Optional[str]=None
