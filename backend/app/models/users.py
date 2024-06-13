from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


# usersテーブルを定義
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(256), nullable=False, index=True)
    email = Column(String(256), nullable=False, unique=True, index=True)
    password = Column(String(256), nullable=False)

    files = relationship("File", back_populates="user", cascade="delete")
    outputs = relationship("Output", back_populates="user", cascade="delete")
