from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.dependencies import get_db

from app.services.chat_service import (
    create_session,
    save_message,
    get_chat_sessions,
    get_chat_history
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


class ChatRequest(BaseModel):

    user_id: int
    session_id: int | None = None
    question: str
    answer: str


@router.post("/save")
def save_chat(
    data: ChatRequest,
    db: Session = Depends(get_db)
):

    session_id = data.session_id

    if session_id is None:

        session = create_session(
            db=db,
            user_id=data.user_id,
            question=data.question
        )

        session_id = session.id_session

    save_message(
        db=db,
        session_id=session_id,
        sender="user",
        text=data.question
    )

    save_message(
        db=db,
        session_id=session_id,
        sender="bot",
        text=data.answer
    )

    return {

        "message":"Chat saved",

        "session_id":session_id

    }



class SessionCreate(BaseModel):

    user_id: int
    session_title: str | None = None


@router.post("/session")
def create_chat_session(
    data: SessionCreate,
    db: Session = Depends(get_db)
):

    session = create_session(
        db=db,
        user_id=data.user_id,
        question=(data.session_title or "")
    )

    return {
        "message": "Session created",
        "session_id": session.id_session
    }


@router.get("/sessions/{user_id}")
def list_chat_sessions(
    user_id: int,
    db: Session = Depends(get_db)
):

    sessions = get_chat_sessions(
        db=db,
        user_id=user_id
    )

    return [
        {
            "session_id": session.id_session,
            "user_id": session.id_user,
            "session_title": session.session_title,
            "created_at": session.created_at,
        }
        for session in sessions
    ]


@router.get("/history/{session_id}")
def get_chat_history_by_session(
    session_id: int,
    db: Session = Depends(get_db)
):

    result = get_chat_history(
        db=db,
        session_id=session_id
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    return {
        "session": {
            "session_id": result["session"].id_session,
            "user_id": result["session"].id_user,
            "session_title": result["session"].session_title,
            "created_at": result["session"].created_at,
        },
        "messages": [
            {
                "message_id": message.id_message,
                "session_id": message.id_session,
                "sender": message.sender,
                "message_text": message.message_text,
                "created_at": message.created_at,
            }
            for message in result["messages"]
        ]
    }