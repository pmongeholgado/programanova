from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from .db import get_db
from .models import Chat

router = APIRouter()


@router.get("/{user_id}")
def list_chats(user_id: int, db: Session = Depends(get_db)):

    chats = db.query(Chat).filter(Chat.user_id == user_id).all()

    return chats


@router.post("/create")
def create_chat(user_id: int, title: str = "Nuevo chat", db: Session = Depends(get_db)):

    chat = Chat(
        title=title,
        user_id=user_id,
        created_at=datetime.utcnow()
    )

    db.add(chat)
    db.commit()
    db.refresh(chat)

    return chat


@router.put("/{chat_id}")
def rename_chat(chat_id: int, title: str, db: Session = Depends(get_db)):

    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        return {"error": "chat no encontrado"}

    chat.title = title

    db.commit()

    return {"status": "chat renombrado"}


@router.delete("/{chat_id}")
def delete_chat(chat_id: int, db: Session = Depends(get_db)):

    chat = db.query(Chat).filter(Chat.id == chat_id).first()

    if not chat:
        return {"error": "chat no encontrado"}

    db.delete(chat)
    db.commit()

    return {"status": "chat eliminado"}