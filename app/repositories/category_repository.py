from app.models.category_model import Category
from app.models.document_model import Document


def get_all_categories(
    db
):

    return (
        db.query(
            Category
        )
        .all()
    )


def get_category_by_id(
    db,
    category_id:int
):

    return (
        db.query(
            Category
        )
        .filter(
            Category.id_category
            ==
            category_id
        )
        .first()
    )


def create_category(
    db,
    category
):

    db.add(
        category
    )
    db.commit()
    db.refresh(
        category
    )
    return category


def update_category(
    db,
    category,
    update_data:dict
):

    for key, value in update_data.items():
        setattr(
            category,
            key,
            value
        )

    db.commit()
    db.refresh(
        category
    )
    return category


def category_has_documents(
    db,
    category_id:int
):

    return (
        db.query(
            Document
        )
        .filter(
            Document.id_category
            ==
            category_id
        )
        .first()
        is not None
    )


def delete_category(
    db,
    category
):

    db.delete(
        category
    )
    db.commit()
