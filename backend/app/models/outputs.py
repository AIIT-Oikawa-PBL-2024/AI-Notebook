from sqlalchemy import TEXT, Column, DateTime, Integer, String

from app.database import Base


class Output(Base):
    """
    出力データを表すクラス。

    :param id: 出力のID
    :type id: int
    :param user_id: ユーザーのID（Firebase UID）
    :type user_id: str
    :param output: 出力データ
    :type output: str
    :param created_at: 作成日時
    :type created_at: datetime
    """

    __tablename__ = "outputs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(String(128), nullable=False, index=True)
    output = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=False)
