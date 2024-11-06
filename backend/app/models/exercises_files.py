from sqlalchemy import Column, ForeignKey, Integer, Table

from app.database import Base

exercise_file = Table(
    "exercise_file",
    Base.metadata,
    Column("exercise_id", Integer, ForeignKey("exercises.id"), primary_key=True),
    Column("file_id", Integer, ForeignKey("files.id"), primary_key=True),
)
