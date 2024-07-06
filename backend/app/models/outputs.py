from sqlalchemy import TEXT, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import relationship

from app.database import Base


# Ouputテーブルのモデルを定義
class Output(Base):
    """
    出力データを表すクラスです。

    Attributes:
        id (int): 出力のID。
        user_id (int): ユーザーのID。外部キー制約があります。
        output (str): 出力データ。
        created_at (datetime): 作成日時。
        user (User): ユーザーとの関連。

    """

    __tablename__ = "outputs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # 外部キー制約を追加
    output = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="outputs")
