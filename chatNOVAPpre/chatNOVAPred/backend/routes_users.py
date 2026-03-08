from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .db import get_db
from .models import User

router = APIRouter()


@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "usuario no encontrado"}

    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "preferences": user.preferences,
        "context": user.context
    }


@router.put("/{user_id}")
def update_user(user_id: int, data: dict, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return {"error": "usuario no encontrado"}

    if "name" in data:
        user.name = data["name"]

    if "preferences" in data:
        user.preferences = data["preferences"]

    if "context" in data:
        user.context = data["context"]

    db.commit()

    return {"status": "usuario actualizado"}