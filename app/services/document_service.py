import mimetypes
import os
import shutil
import uuid
import re
from io import BytesIO
from typing import List, Dict, Any

from fastapi import HTTPException
from fastapi import status
from fastapi import UploadFile
from fastapi.responses import FileResponse

from pypdf import PdfReader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document as LCDocument

from app.models.document_model import Document
from app.models.document_chunk_model import DocumentChunk

from app.repositories.document_repository import (

    create_document,
    get_document_by_id,
    get_all_documents,
    get_documents_by_category,
    update_document as repo_update_document,
    delete_chunks_by_document_id,
    delete_document as repo_delete_document

)

from app.config import UPLOAD_FOLDER, VECTORSTORE_FOLDER, EMBEDDING_MODEL
from app.database import SessionLocal

UPLOAD_DIR = os.path.join(UPLOAD_FOLDER, "documents")

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


# Global variable for lazy-loaded embeddings
_embeddings = None


def get_embeddings():
    """Get or initialize embeddings (lazy-loaded)."""
    global _embeddings
    if _embeddings is None:
        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            encode_kwargs={"normalize_embeddings": True},
        )
    return _embeddings


def _clean_text(text: str) -> str:
    """Clean extracted text from PDF."""
    text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)
    text = re.sub(r" {2,}", " ", text)
    return text.strip()


def _extract_ayat(pasal_text: str) -> List[Dict[str, Any]]:
    """Extract ayat (verses) from pasal (article) text."""
    if not pasal_text.strip():
        return []

    ayat_pattern = re.compile(r"(?:^|(?<=\n))\s*\((\d+)\)\s*")
    matches = list(ayat_pattern.finditer(pasal_text))

    if not matches:
        cleaned = pasal_text.strip()
        return [{"nomor": 1, "isi": cleaned}] if cleaned else []

    ayat_list = []
    for i, match in enumerate(matches):
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(pasal_text)
        isi = pasal_text[start:end].strip()
        if isi:
            ayat_list.append({"nomor": int(match.group(1)), "isi": isi})
    return ayat_list


def parse_legal_pdf(pages_text: List[tuple], sumber: str = "") -> List[Dict[str, Any]]:
    """Parse legal document PDF into structured format with BAB, Pasal, and Ayat."""
    bab_re = re.compile(r"BAB\s+[IVXLCDM]+(?:[ \t]+[A-Z][A-Z ]*|\s*\n\s*[A-Z][A-Z ]*)?")
    pasal_re = re.compile(r"Pasal\s+\d+[A-Za-z]?")

    current_bab = None
    current_pasal = None
    current_bab_halaman = 1
    current_pasal_halaman = 1
    current_text = ""
    raw_pasal_list = []

    for page_num, raw_text in pages_text:
        text = _clean_text(raw_text)
        markers = []
        
        for m in bab_re.finditer(text):
            raw = m.group().strip()
            cleaned_bab = re.sub(r"\s*\n\s*", " ", raw)
            markers.append((m.start(), m.end(), "bab", cleaned_bab))
        
        for m in pasal_re.finditer(text):
            markers.append((m.start(), m.end(), "pasal", m.group().strip()))
        
        markers.sort(key=lambda x: x[0])

        if not markers:
            current_text += "\n" + text
            continue

        if markers[0][0] > 0:
            pre = text[:markers[0][0]].strip()
            if pre:
                current_text += "\n" + pre

        for i, (start, end, mtype, value) in enumerate(markers):
            next_start = markers[i + 1][0] if i + 1 < len(markers) else len(text)
            
            if mtype == "bab":
                if current_pasal and current_text.strip():
                    raw_pasal_list.append({
                        "bab": current_bab,
                        "pasal": current_pasal,
                        "halaman": current_pasal_halaman,
                        "text": current_text.strip(),
                    })
                    current_pasal = None
                    current_text = ""
                elif current_pasal:
                    current_pasal = None
                    current_text = ""
                else:
                    current_text = ""
                
                current_bab = value
                current_bab_halaman = page_num
            
            elif mtype == "pasal":
                if current_pasal:
                    raw_pasal_list.append({
                        "bab": current_bab,
                        "pasal": current_pasal,
                        "halaman": current_pasal_halaman,
                        "text": current_text.strip(),
                    })
                
                current_pasal = value
                current_pasal_halaman = page_num
                current_text = ""

            between = text[end:next_start].strip()
            if between:
                current_text += "\n" + between

    if current_pasal:
        raw_pasal_list.append({
            "bab": current_bab,
            "pasal": current_pasal,
            "halaman": current_pasal_halaman,
            "text": current_text.strip(),
        })

    result = []
    for item in raw_pasal_list:
        ayat_list = _extract_ayat(item["text"])
        if not ayat_list:
            continue
        result.append({
            "sumber": sumber,
            "bab": item["bab"],
            "pasal": item["pasal"],
            "halaman": item["halaman"],
            "ayat": ayat_list,
        })
    
    return result


def load_vectorstore():
    """Load FAISS vectorstore from disk."""
    index_path = os.path.join(VECTORSTORE_FOLDER, "faiss.index")
    if os.path.exists(index_path):
        return FAISS.load_local(VECTORSTORE_FOLDER, get_embeddings(), index_name="faiss", allow_dangerous_deserialization=True)
    return None


def save_vectorstore(vectorstore):
    """Save FAISS vectorstore to disk."""
    os.makedirs(VECTORSTORE_FOLDER, exist_ok=True)
    vectorstore.save_local(VECTORSTORE_FOLDER, index_name="faiss")


def ingest_pdf(file_bytes: bytes, filename: str, title: str = None, user_id: int = 0, id_category: int = 0) -> Dict[str, Any]:
    """Ingest PDF file and create chunks with vector embeddings."""
    if title is None:
        title = filename
    if not filename.lower().endswith(".pdf"):
        raise ValueError("Hanya file PDF yang didukung")

    pdf = PdfReader(BytesIO(file_bytes))
    if pdf.is_encrypted:
        raise ValueError("PDF terenkripsi tidak didukung")

    pages_text = []
    for page_num, page in enumerate(pdf.pages, start=1):
        text = page.extract_text() or ""
        pages_text.append((page_num, text))

    if not any(text for _, text in pages_text):
        raise ValueError("PDF tidak mengandung teks")

    structured_data = parse_legal_pdf(pages_text, sumber=filename)
    if not structured_data:
        raise ValueError("Gagal mem-parsing isi PDF")

    db = SessionLocal()
    
    try:
        document = Document(
            title=title, 
            file_name=filename, 
            file_path="", 
            uploaded_by=user_id, 
            id_category=id_category
        )
        db.add(document)
        db.commit()
        db.refresh(document)

        chunk_counter = db.query(DocumentChunk).count()
        lc_docs = []

        for item in structured_data:
            for ayat_item in item.get("ayat", []):
                isi = ayat_item.get("isi", "").strip()
                if not isi:
                    continue

                chunk = DocumentChunk(
                    id_document=document.id_document,
                    chunk_index=chunk_counter,
                    bab=item.get("bab"),
                    pasal=item.get("pasal"),
                    ayat=ayat_item.get("nomor"),
                    halaman=item.get("halaman"),
                    content=isi,
                )
                db.add(chunk)
                lc_docs.append(LCDocument(
                    page_content=isi,
                    metadata={
                        "document_id": document.id_document,
                        "bab": item.get("bab") or "",
                        "pasal": item.get("pasal") or "",
                        "ayat": ayat_item.get("nomor") or 0,
                        "halaman": item.get("halaman") or 0,
                    },
                ))
                chunk_counter += 1

        db.commit()

        vectorstore = load_vectorstore()
        if lc_docs:
            if vectorstore is None:
                vectorstore = FAISS.from_documents(lc_docs, get_embeddings())
            else:
                vectorstore.add_documents(lc_docs)
            save_vectorstore(vectorstore)

        return {
            "message": "Dokumen berhasil diupload dan diindex",
            "document_id": document.id_document,
            "total_chunks": len(lc_docs),
        }
    
    finally:
        db.close()