from sqlalchemy import TEXT, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base
from app.models.exercises import Exercise


class ExerciseUserAnswer(Base):
    """
    ユーザーの回答を表すクラス。

    :param id: 回答のID
    :type id: int
    :param exercise_id: 練習問題のID
    :type exercise_id: int
    :param user_id: ユーザーのID（Firebase UID）
    :type user_id: str
    :param answer: ユーザーの回答
    :type answer: str
    :param scoring_results: 採点結果
    :type scoring_results: str
    :param created_at: 回答日時
    :type created_at: datetime
    """

    __tablename__ = "exercise_user_answers"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False, index=True)
    user_id = Column(String(128), nullable=False, index=True)
    answer = Column(TEXT, nullable=False)
    scoring_results = Column(TEXT, nullable=True)
    created_at = Column(DateTime, nullable=False)

    # リレーションシップの定義
    exercise = relationship("Exercise", back_populates="answers")


# Exerciseモデルにリレーションシップを追加
Exercise.answers = relationship(
    "ExerciseUserAnswer", back_populates="exercise", cascade="all, delete-orphan"
)
