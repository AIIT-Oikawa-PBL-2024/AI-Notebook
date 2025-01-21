from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Optional

from app.schemas.files import File


class OutputBase(BaseModel):
    """
    出力のベースモデル。

    :param title: 出力のタイトル
    :type title: str
    :param output: 出力の文字列
    :type output: str
    :param style: 出力のスタイル
    :type style: str
    """

    title: str
    output: str
    style: Optional[str]


class OutputCreate(OutputBase):
    """
    OutputBaseクラスを継承した出力データの作成を表すクラス。

    :param user_id: ユーザーID
    :type user_id: str
    :param created_at: 作成日時
    :type created_at: datetime
    """

    user_id: str
    created_at: datetime
    file_names: List[str] = Field(default_factory=list, description="関連するファイル名のリスト")
    style: str


class Output(OutputCreate):
    """
    OutputCreateクラスを継承した出力データの取得を表すクラス。

    :param id: 出力のID
    :type id: int
    :param model_config: モデルの設定辞書
    :type model_config: ConfigDict
    """

    id: int

    model_config = ConfigDict(from_attributes=True)


class OutputRead(OutputBase):
    """
    OutputBaseクラスを継承した出力データの取得を表すクラス。

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
    style: Optional[str] = Field(..., description="出力のスタイル", max_length=10)

    model_config = ConfigDict(from_attributes=True)


class OutputRequest(BaseModel):
    files: list[str]
    title: str
    style: str
