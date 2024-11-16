from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OutputBase(BaseModel):
    """
    出力のベースモデル。

    :param output: 出力の文字列
    :type output: str
    """

    output: str


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
