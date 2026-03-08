from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from .db import get_db
from .models import Message

router = APIRouter()


@router.get("/{chat_id}")
def list_messages(chat_id: int, db: Session = Depends(get_db)):

    messages = db.query(Message).filter(Message.chat_id == chat_id).all()

    return messages


@router.post("/create")
def create_message(chat_id: int, role: str, content: str, db: Session = Depends(get_db)):

    message = Message(
        chat_id=chat_id,
        role=role,
        content=content,
        created_at=datetime.utcnow()
    )

    db.add(message)
    db.commit()
    db.refresh(message)

    return message