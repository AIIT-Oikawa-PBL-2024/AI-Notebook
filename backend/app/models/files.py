from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db import Base


# filesテーブルを定義
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(256), nullable=False, index=True)
    file_path = Column(String(512), nullable=False)
    file_size = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, nullable=False)


