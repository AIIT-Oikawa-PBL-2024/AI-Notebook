from sqlalchemy import TEXT, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.outputs_files import output_file


class Output(Base):
    """
    出力データを表すクラス。

    :param id: 出力のID
    :type id: int
    :param title: 出力のタイトル
    :type id: str
    :param user_id: ユーザーのID（Firebase UID）
    :type user_id: str
    :param output: 出力データ
    :type output: str
    :param created_at: 作成日時
    :type created_at: datetime
    """

    __tablename__ = "outputs"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(100), nullable=False)
    user_id = Column(String(128), nullable=False, index=True)
    style = Column(String(10), nullable=True)
    output = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=False)

    # リレーションシップの定義
    files = relationship("File", secondary=output_file, back_populates="outputs")
