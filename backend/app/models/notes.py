from sqlalchemy import Column, DateTime, Integer, String, Text, func

from app.database import Base


class Note(Base):
    """
    ユーザーのノートを表すモデルクラス

    :param id: ノートの一意なID。
    :type id: Integer
    :param user_id: このノートを所有するユーザーのID。
    :type user_id: String
    :param title: ノートのタイトル。
    :type title: String
    :param content: ノートの内容。
    :type content: Text
    :param created_at: ノートが作成された日時。
    :type created_at: DateTime
    :param updated_at: ノートが最後に更新された日時。
    :type updated_at: DateTime
    :param user: このノートを所有するユーザーへのリレーションシップ。
    :type user: relationship
    """

    __tablename__ = "notes"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id = Column(
        String(128), nullable=False, index=True
    )  # Firebase UIDの最大長に合わせて調整
    title = Column(String(256), nullable=False, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )
