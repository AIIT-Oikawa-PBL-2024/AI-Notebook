from datetime import datetime

from pydantic import BaseModel, Field


class ExerciseUserAnswerBase(BaseModel):
    """
    ユーザーの回答のベースモデル。

    :param answer: ユーザーの回答
    :type answer: str
    """

    answer: str = Field(..., description="ユーザーの回答")
    scoring_results: str = Field(..., description="採点結果")


class ExerciseUserAnswerCreate(ExerciseUserAnswerBase):
    """
    ユーザーの回答作成用モデル。

    :param exercise_id: 練習問題のID
    :type exercise_id: int
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :param created_at: 回答日時
    :type created_at: datetime
    """

    exercise_id: int = Field(..., description="練習問題のID")
    user_id: str = Field(..., description="ユーザーのFirebase UID", max_length=128)
    created_at: datetime = Field(default_factory=datetime.now, description="回答日時")


class ExerciseUserAnswerRead(ExerciseUserAnswerBase):
    """
    ユーザーの回答取得用モデル。

    :param id: 回答のID
    :type id: int
    :param exercise_id: 練習問題のID
    :type exercise_id: int
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :param created_at: 回答日時
    :type created_at: datetime
    """

    id: int = Field(..., description="回答のID")
    exercise_id: int = Field(..., description="練習問題のID")
    user_id: str = Field(..., description="ユーザーのFirebase UID", max_length=128)
    created_at: datetime = Field(..., description="回答日時")
