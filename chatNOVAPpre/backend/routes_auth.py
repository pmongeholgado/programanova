from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .db import get_db
from .models import User
from .auth import hash_password, verify_password, create_access_token

router = APIRouter()


@router.post("/register")
def register(email: str, password: str, db: Session = Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == email).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")

    user = User(
        email=email,
        password_hash=hash_password(password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"status": "usuario creado"}


@router.post("/login")
def login(email: str, password: str, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")

    token = create_access_token({"user_id": user.id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }