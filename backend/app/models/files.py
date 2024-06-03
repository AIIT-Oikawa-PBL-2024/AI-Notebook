from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


# filesテーブルを定義
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file_name = Column(String(256), nullable=False, index=True)
    file_size = Column(Integer, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # 外部キー制約を追加
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="files")
