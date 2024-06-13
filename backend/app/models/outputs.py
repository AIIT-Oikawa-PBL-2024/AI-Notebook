from sqlalchemy import TEXT, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


# Ouputテーブルのモデルを定義
class Output(Base):
    __tablename__ = "outputs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # 外部キー制約を追加
    output = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="outputs")
