from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import (
    engine,
    Base
)

from app.models.document_chunk_model import DocumentChunk

from app.routers import (
    auth_router,
    document_router,
    chat_router,
    category_router
)

# Create tables
Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title=
    "Chatbot Peraturan Pendidikan Tinggi API",
    version=
    "1.0.0"
)


# CORS
app.add_middleware(

    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Authentication routes
app.include_router(
    auth_router.router
)

# Document routes
app.include_router(
    document_router.router
)

# Chat routes
app.include_router(
    chat_router.router
)

# Category routes
app.include_router(
    category_router.router
)


@app.get("/")
def home():

    return {
        "message":
        "Backend running"
    }