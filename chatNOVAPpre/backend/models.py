from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    email = Column(String, unique=True, index=True)
    password_hash = Column(String)

    # memoria básica usuario
    name = Column(String, nullable=True)
    preferences = Column(Text, nullable=True)
    context = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    chats = relationship("Chat", back_populates="user")


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, default="Nuevo chat")

    created_at = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="chats")
    messages = relationship("Message", back_populates="chat")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)

    role = Column(String)  # user o assistant
    content = Column(Text)

    created_at = Column(DateTime, default=datetime.utcnow)

    chat_id = Column(Integer, ForeignKey("chats.id"))

    chat = relationship("Chat", back_populates="messages")