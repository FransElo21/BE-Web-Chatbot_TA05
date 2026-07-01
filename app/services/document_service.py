import mimetypes
import os
import shutil
import uuid

from fastapi import HTTPException
from fastapi import status
from fastapi import UploadFile
from fastapi.responses import FileResponse

from app.models.document_model import Document

from app.repositories.document_repository import (

    create_document,
    get_document_by_id,
    get_all_documents,
    get_documents_by_category,
    update_document as repo_update_document,
    delete_chunks_by_document_id,
    delete_document as repo_delete_document

)

UPLOAD_DIR="uploads/documents"

def upload_document(
    db,
    title:str,
    id_category:int,
    file:UploadFile,
    user_id:int
):

    os.makedirs(
        UPLOAD_DIR,
        exist_ok=True
    )

    extension=(

        os.path.splitext(
            file.filename
        )[1]

    )

    unique_filename=(

        f"{uuid.uuid4()}"
        f"{extension}"
    )

    file_path=os.path.join(
        UPLOAD_DIR,
        unique_filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    document=Document(
        title=title,
        file_name=file.filename,
        file_path=file_path,
        uploaded_by=user_id,
        id_category=id_category
    )

    return create_document(
        db,
        document
    )


def detail_document(
    db,
    document_id

):
    return get_document_by_id(
        db,
        document_id
    )


def get_documents(
    db
):
    return get_all_documents(
        db
    )

def document_by_category(
    db,
    category_id
):

    return get_documents_by_category(
        db,
        category_id
    )


def _get_document_file_response(
    db,
    document_id:int,
    disposition_type:str
):

    document=get_document_by_id(
        db,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if not os.path.exists(
        document.file_path
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document file not found"
        )

    media_type, _=mimetypes.guess_type(
        document.file_path
    )

    return FileResponse(
        path=document.file_path,
        media_type=media_type or "application/octet-stream",
        filename=document.file_name,
        content_disposition_type=disposition_type
    )


def download_document(
    db,
    document_id:int
):

    return _get_document_file_response(
        db,
        document_id,
        "attachment"
    )


def preview_document(
    db,
    document_id:int
):

    return _get_document_file_response(
        db,
        document_id,
        "inline"
    )


def update_document(
    db,
    document_id:int,
    title:str=None,
    id_category:int=None,
    file:UploadFile=None
):

    document=get_document_by_id(
        db,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    if title is not None:
        document.title=title

    if id_category is not None:
        document.id_category=id_category

    if file is not None and file.filename:

        old_path=document.file_path

        extension=(
            os.path.splitext(
                file.filename
            )[1]
        )

        unique_filename=(
            f"{uuid.uuid4()}"
            f"{extension}"
        )

        file_path=os.path.join(
            UPLOAD_DIR,
            unique_filename
        )

        with open(
            file_path,
            "wb"
        ) as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        document.file_name=file.filename
        document.file_path=file_path

        if old_path and os.path.exists(
            old_path
        ):
            os.remove(
                old_path
            )

    db.commit()
    db.refresh(
        document
    )

    return document


def delete_document(
    db,
    document_id:int
):

    document=get_document_by_id(
        db,
        document_id
    )

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )

    file_path=document.file_path

    delete_chunks_by_document_id(
        db,
        document_id
    )

    repo_delete_document(
        db,
        document
    )

    if file_path and os.path.exists(
        file_path
    ):
        os.remove(
            file_path
        )

    return {"message":"Document deleted"}