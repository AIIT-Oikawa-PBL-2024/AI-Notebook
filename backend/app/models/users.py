from sqlalchemy import Column, Integer, String

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False, index=True)
    email = Column(String(256), nullable=False, unique=True, index=True)
    password = Column(String(256), nullable=False)
