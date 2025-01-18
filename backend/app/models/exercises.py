from sqlalchemy import TEXT, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.exercises_files import exercise_file


class Exercise(Base):
    """
    出力データを表すクラス。

    :param id: 出力のID
    :type id: int
    :param user_id: ユーザーのID（Firebase UID）
    :type user_id: str
    :param response: 出力データ
    :type response: str
    :param created_at: 作成日時
    :type created_at: datetime
    :param exercise_type: 練習問題の種類
    :type exercise_type: str
    :param title: 練習問題のタイトル
    :type title: str
    :param difficulty: 練習問題の難易度
    :type difficulty: str
    """

    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    title = Column(String(100), nullable=False)
    response = Column(TEXT, nullable=False)
    created_at = Column(DateTime, nullable=False)
    exercise_type = Column(String(128), nullable=False)
    user_id = Column(String(128), nullable=False, index=True)
    difficulty = Column(String(10), nullable=True)

    # リレーションシップの定義
    files = relationship("File", secondary=exercise_file, back_populates="exercises")
