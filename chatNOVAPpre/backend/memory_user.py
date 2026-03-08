from sqlalchemy.orm import Session
from .models import User


def get_user_memory(user_id: int, db: Session):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    return {
        "user_id": user.id,
        "email": user.email,
        "name": user.name,
        "preferences": user.preferences,
        "context": user.context
    }


def update_user_memory(user_id: int, data: dict, db: Session):

    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        return None

    if "name" in data:
        user.name = data["name"]

    if "preferences" in data:
        user.preferences = data["preferences"]

    if "context" in data:
        user.context = data["context"]

    db.commit()

    return True