from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NoteBase(BaseModel):
    """
    ノートの基本クラス

    :param BaseModel: ベースモデル
    :type BaseModel: BaseModel
    :ivar title: ノートのタイトル
    :vartype title: str
    :ivar content: ノートの内容
    :vartype content: str
    """

    title: str
    content: str


class NoteResponse(NoteBase):
    """
    ノートのレスポンス用クラス

    :param NoteBase: ノートの基本クラス
    :type NoteBase: NoteBase
    :ivar id: ノートのID
    :vartype id: int
    :ivar model_config: モデルの設定
    :vartype model_config: ConfigDict
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


class NoteByCurrentUserResponse(NoteBase):
    """
    現在のユーザーによるノートのレスポンス用クラス

    :param NoteBase: ノートの基本クラス
    :type NoteBase: NoteBase
    :ivar id: ノートのID
    :vartype id: int
    :ivar user_id: ユーザーID
    :vartype user_id: str
    :ivar created_at: ノートの作成日時
    :vartype created_at: datetime
    :ivar updated_at: ノートの更新日時
    :vartype updated_at: datetime
    :ivar model_config: モデルの設定
    :vartype model_config: ConfigDict
    """

    id: int
    user_id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class NoteCreate(NoteBase):
    """
    ノート作成用のクラス

    :param NoteBase: ノートの基本クラス
    :type NoteBase: NoteBase
    :ivar user_id: ユーザーID
    :vartype user_id: str
    """

    user_id: str


class NoteCreateResponse(NoteCreate):
    """
    ノート作成のレスポンス用クラス

    :param NoteCreate: ノート作成用のクラス
    :type NoteCreate: NoteCreate
    :ivar id: ノートのID
    :vartype id: int
    :ivar model_config: モデルの設定
    :vartype model_config: ConfigDict
    """

    id: int
    model_config = ConfigDict(from_attributes=True)


class NoteUpdate(NoteBase):
    """
    ノート更新用のクラス

    :param NoteBase: ノートの基本クラス
    :type NoteBase: NoteBase
    """

    pass


class NoteUpdateResponse(NoteUpdate):
    """
    ノート更新のレスポンス用クラス

    :param NoteUpdate: ノート更新用のクラス
    :type NoteUpdate: NoteUpdate
    :ivar id: ノートのID
    :vartype id: int
    :ivar model_config: モデルの設定
    :vartype model_config: ConfigDict
    """

    id: int
    user_id: str
    model_config = ConfigDict(from_attributes=True)
