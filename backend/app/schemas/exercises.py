from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.files import File


class ExerciseRequest(BaseModel):
    files: list[str]
    title: str
    difficulty: str


class ExerciseBase(BaseModel):
    """
    出力のベースモデル。

    :param response: 出力の文字列
    :type response: str
    :param exercise_type: 練習問題の種類
    :type exercise_type: str
    :param title: 練習問題のタイトル
    :type title: str
    """

    response: str = Field(..., description="出力の文字列")
    exercise_type: str = Field(..., description="練習問題の種類")
    title: str = Field(..., description="練習問題のタイトル", max_length=100)


class ExerciseCreate(ExerciseBase):
    """
    ExerciseBaseクラスを継承した出力データの作成を表すクラス。

    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :param created_at: 作成日時
    :type created_at: datetime
    :param file_names: 関連するファイル名のリスト
    :type file_names: List[str]
    :param difficulty: 練習問題の難易度
    :type difficulty: str
    """

    user_id: str = Field(..., description="ユーザーのFirebase UID", max_length=128)
    created_at: datetime = Field(default_factory=datetime.now, description="作成日時")
    file_names: List[str] = Field(default_factory=list, description="関連するファイル名のリスト")
    difficulty: str = Field(..., description="練習問題の難易度", max_length=10)


class ExerciseRead(ExerciseBase):
    """
    ExerciseBaseクラスを継承した出力データの取得を表すクラス。

    :param id: 出力のID
    :type id: int
    :param user_id: ユーザーID（Firebase UID）
    :type user_id: str
    :param created_at: 作成日時
    :type created_at: datetime
    :param files: 関連するファイル情報のリスト
    :type files: List[FileBase]
    """

    id: int = Field(..., description="出力データのID")
    user_id: str = Field(..., description="ユーザーのFirebase UID", max_length=128)
    created_at: datetime = Field(..., description="作成日時")
    files: List[File] = Field(default_factory=list, description="関連するファイル情報のリスト")

    model_config = ConfigDict(from_attributes=True)
