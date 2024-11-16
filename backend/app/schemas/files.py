from datetime import datetime

from pydantic import BaseModel, ConfigDict


class FileBase(BaseModel):
    """
    基本的なファイル情報を表すモデル。

    :param file_name: ファイルの名前
    :type file_name: str
    :param file_size: ファイルのサイズ（バイト単位）
    :type file_size: int
    """

    file_name: str
    file_size: int


class FileCreate(FileBase):
    """
    FileBaseクラスを継承したファイル作成を表すクラス。

    :param user_id: ユーザーID
    :type user_id: str
    :param created_at: 作成日時
    :type created_at: datetime
    """

    user_id: str
    created_at: datetime


class File(FileBase):
    """
    FileBaseクラスを継承したファイル情報の取得を表すクラス。

    :param id: ファイルのID
    :type id: int
    :param user_id: ユーザーID
    :type user_id: str
    :param created_at: 作成日時
    :type created_at: datetime
    :param model_config: モデルの設定辞書
    :type model_config: ConfigDict
    """

    id: int
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
