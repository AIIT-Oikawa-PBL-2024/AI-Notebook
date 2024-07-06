from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OutputBase(BaseModel):
    """
    OutputBaseクラスは、出力のベースモデルです。

    Attributes:
        output (str): 出力の文字列です。
    """

    output: str


class OutputCreate(OutputBase):
    """
    OutputCreateクラスは、OutputBaseクラスを継承した出力データの作成を表します。

    :param user_id: ユーザーID
    :type user_id: int
    :param created_at: 作成日時
    :type created_at: datetime
    """

    user_id: int
    created_at: datetime


# 学習帳作成時のレスポンス
class Output(OutputCreate):
    """
    Output クラスは OutputCreate クラスを継承しています。

    :param id: 出力のID
    :type id: int
    :param model_config: モデルの設定辞書
    :type model_config: ConfigDict
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
