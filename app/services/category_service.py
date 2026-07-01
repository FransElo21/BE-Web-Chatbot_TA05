from fastapi import HTTPException
from fastapi import status

from app.models.category_model import Category

from app.repositories.category_repository import (
    get_all_categories,
    get_category_by_id,
    create_category as repo_create_category,
    update_category as repo_update_category,
    category_has_documents,
    delete_category as repo_delete_category
)


def get_categories(
    db
):
    return get_all_categories(
        db
    )


def get_category(
    db,
    category_id:int
):

    category=get_category_by_id(
        db,
        category_id
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    return category


def create_category(
    db,
    name:str,
    description:str=None
):

    category=Category(
        name=name,
        description=description
    )

    return repo_create_category(
        db,
        category
    )


def update_category(
    db,
    category_id:int,
    update_data:dict
):

    category=get_category_by_id(
        db,
        category_id
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    filtered_data={
        key:value
        for key, value in update_data.items()
        if value is not None
    }

    if not filtered_data:
        return category

    return repo_update_category(
        db,
        category,
        filtered_data
    )


def delete_category(
    db,
    category_id:int
):

    category=get_category_by_id(
        db,
        category_id
    )

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )

    if category_has_documents(
        db,
        category_id
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Kategori masih digunakan oleh dokumen"
        )

    repo_delete_category(
        db,
        category
    )
