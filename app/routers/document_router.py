from typing import Optional

from fastapi import APIRouter
from fastapi import Depends
from fastapi import File
from fastapi import Form
from fastapi import UploadFile
from fastapi import HTTPException
from fastapi import status

from sqlalchemy.orm import Session
from app.dependencies import get_db

from app.schemas.document_schema import (
    DocumentResponse,
    UploadResponse
)

from app.services.document_service import (

    upload_document,
    detail_document,
    get_documents,
    document_by_category,
    download_document,
    preview_document,
    update_document,
    delete_document,
    ingest_pdf
)

router=APIRouter(
    prefix="/documents",
    tags=["Documents"]
)

@router.post("/upload", response_model=UploadResponse)
async def upload(

    file: UploadFile = File(...),
    title: str = Form(None),
    user_id: int = Form(0),
    id_category: int = Form(0),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Hanya file PDF yang didukung")

    content = await file.read()
    try:
        # Use title from form if provided, otherwise use filename
        doc_title = title if title else file.filename
        result = ingest_pdf(content, file.filename, title=doc_title, user_id=user_id, id_category=id_category)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return UploadResponse(**result)

@router.get("/")
def get_all(

    db:Session=
    Depends(get_db)
):

    return get_documents(
        db
    )


@router.get("/download/{document_id}")
def download(

    document_id:int,

    db:Session=Depends(get_db)

):

    return download_document(

        db,
        document_id
    )


@router.get("/preview/{document_id}")
def preview(

    document_id:int,

    db:Session=Depends(get_db)

):

    return preview_document(

        db,
        document_id
    )


@router.get("/{document_id}")
def detail(

    document_id:int,

    db:Session=
    Depends(get_db)

):

    return detail_document(

        db,
        document_id
    )


@router.get("/category/{category_id}")
def get_by_category(

    category_id:int,

    db:Session=
    Depends(get_db)

):

    return document_by_category(

        db,
        category_id
    )


@router.put(
    "/{document_id}",
    response_model=dict
)
def update(

    document_id:int,
    title:Optional[str]=Form(None),
    id_category:Optional[int]=Form(None),
    file:Optional[UploadFile]=File(None),
    db:Session=Depends(
        get_db
    )
):

    updated=update_document(
        db,
        document_id,
        title,
        id_category,
        file
    )

    return {
        "status":"success",
        "message":"Dokumen berhasil diperbarui",
        "data":DocumentResponse.model_validate(
            updated
        ).model_dump()
    }


@router.delete(
    "/{document_id}",
    response_model=dict
)
def delete(

    document_id:int,
    db:Session=Depends(
        get_db
    )
):

    delete_document(
        db,
        document_id
    )

    return {
        "status":"success",
        "message":"Dokumen berhasil dihapus"
    }