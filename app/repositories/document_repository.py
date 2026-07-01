from app.models.document_model import Document
from app.models.document_chunk_model import DocumentChunk


def create_document(
    db,
    document
):

    db.add(
        document
    )
    db.commit()
    db.refresh(
        document
    )
    return document

def get_document_by_id(
    db,
    document_id:int

):

    return (
        db.query(
            Document
        )

        .filter(
            Document.id_document
            ==
            document_id
        )

        .first()
    )

def get_all_documents(
    db
):

    return (
        db.query(
            Document
        )
        .all()
    )

def get_documents_by_category(

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
        .all()
    )


def update_document(
    db,
    document,
    update_data:dict
):

    for key, value in update_data.items():
        setattr(
            document,
            key,
            value
        )

    db.commit()
    db.refresh(
        document
    )
    return document


def delete_chunks_by_document_id(
    db,
    document_id:int
):

    db.query(
        DocumentChunk
    ).filter(
        DocumentChunk.id_document
        ==
        document_id
    ).delete()

    db.commit()


def delete_document(
    db,
    document
):

    db.delete(
        document
    )
    db.commit()