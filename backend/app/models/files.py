from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


# filesテーブルを定義
class File(Base):
    """
    ファイル情報を格納するためのSQLAlchemyモデルクラス。

    :param id: ファイルの一意の識別子
    :type id: int
    :param file_name: ファイルの名前
    :type file_name: str
    :param file_size: ファイルのサイズ（バイト単位）
    :type file_size: int
    :param user_id: ファイルを所有するユーザーのID
    :type user_id: int
    :param created_at: ファイルの作成日時
    :type created_at: datetime
    :param user: ファイルを所有するユーザーとのリレーションシップ
    :type user: User
    """

    __tablename__ = "files"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    file_name = Column(String(256), nullable=False, index=True)
    file_size = Column(Integer, nullable=False)
    user_id = Column(
        Integer, ForeignKey("users.id"), nullable=False
    )  # 外部キー制約を追加
    created_at = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="files")
