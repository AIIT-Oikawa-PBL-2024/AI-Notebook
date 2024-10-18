from sqlalchemy import Column, DateTime, Integer, String

from app.database import Base


class File(Base):
    """
    ファイル情報を格納するためのSQLAlchemyモデルクラス。

    :param id: ファイルの一意の識別子
    :type id: int
    :param file_name: ファイルの名前
    :type file_name: str
    :param file_size: ファイルのサイズ（バイト単位）
    :type file_size: int
    :param user_id: ファイルを所有するユーザーのFirebase UID
    :type user_id: str
    :param created_at: ファイルの作成日時
    :type created_at: datetime
    """

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file_name = Column(String(256), nullable=False, index=True)
    file_size = Column(Integer, nullable=False)
    user_id = Column(
        String(128), nullable=False, index=True
    )  # Firebase UIDの最大長に合わせて調整
    created_at = Column(DateTime, nullable=False)
