from app.models.chat_session_model import ChatSession
from app.models.chat_message_model import ChatMessage


def create_session(
    db,
    user_id,
    question
):

    session = ChatSession(

        id_user=user_id,
        session_title=question[:30]
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return session


def save_message(
    db,
    session_id,
    sender,
    text
):

    message = ChatMessage(

        id_session=session_id,
        sender=sender,
        message_text=text

    )

    db.add(message)
    db.commit()
    return message


def get_chat_sessions(
    db,
    user_id=None
):

    query = db.query(ChatSession)

    if user_id is not None:
        query = query.filter(ChatSession.id_user == user_id)

    return query.order_by(ChatSession.created_at.desc()).all()


def get_chat_history(
    db,
    session_id
):

    session = (
        db.query(ChatSession)
        .filter(ChatSession.id_session == session_id)
        .first()
    )

    if session is None:
        return None

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.id_session == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    return {
        "session": session,
        "messages": messages,
    }