from fastapi import APIRouter
from fastapi import Depends

from sqlalchemy.orm import Session

from app.dependencies import get_db

from app.schemas.category_schema import (
    CategoryResponse,
    CreateCategoryRequest,
    UpdateCategoryRequest
)

from app.services.category_service import (
    get_categories,
    get_category,
    create_category,
    update_category,
    delete_category
)

router=APIRouter(

    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    "/",
    response_model=list[CategoryResponse]
)
def get_all(

    db:Session=
    Depends(get_db)
):

    return get_categories(
        db
    )


@router.get(
    "/{category_id}",
    response_model=CategoryResponse
)
def get_one(

    category_id:int,
    db:Session=
    Depends(get_db)
):

    return get_category(
        db,
        category_id
    )


@router.post(
    "/",
    status_code=201,
    response_model=dict
)
def create(

    data:CreateCategoryRequest,
    db:Session=
    Depends(get_db)
):

    category=create_category(
        db,
        data.name,
        data.description
    )

    return {
        "status":"success",
        "message":"Kategori berhasil ditambahkan",
        "data":CategoryResponse.model_validate(
            category
        ).model_dump()
    }


@router.put(
    "/{category_id}",
    response_model=dict
)
def update(

    category_id:int,
    data:UpdateCategoryRequest,
    db:Session=
    Depends(get_db)
):

    updated=update_category(
        db,
        category_id,
        data.model_dump(
            exclude_unset=True
        )
    )

    return {
        "status":"success",
        "message":"Kategori berhasil diperbarui",
        "data":CategoryResponse.model_validate(
            updated
        ).model_dump()
    }


@router.delete(
    "/{category_id}",
    response_model=dict
)
def delete(

    category_id:int,
    db:Session=
    Depends(get_db)
):

    delete_category(
        db,
        category_id
    )

    return {
        "status":"success",
        "message":"Kategori berhasil dihapus"
    }
