from sqlalchemy import Column, ForeignKey, Integer, Table

from app.database import Base

output_file = Table(
    "output_file",
    Base.metadata,
    Column("output_id", Integer, ForeignKey("outputs.id"), primary_key=True),
    Column("file_id", Integer, ForeignKey("files.id"), primary_key=True),
)
