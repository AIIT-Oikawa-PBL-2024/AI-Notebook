"""add answers table

Revision ID: d947474f6b3c
Revises:
Create Date: 2024-12-29 14:51:50.554648

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d947474f6b3c"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "answers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("related_files", sa.JSON(), nullable=False),
        sa.Column("question_id", sa.String(length=256), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("choice_a", sa.Text(), nullable=False),
        sa.Column("choice_b", sa.Text(), nullable=False),
        sa.Column("choice_c", sa.Text(), nullable=False),
        sa.Column("choice_d", sa.Text(), nullable=False),
        sa.Column("user_selected_choice", sa.String(length=256), nullable=False),
        sa.Column("correct_choice", sa.String(length=256), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("explanation", sa.Text(), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_answers_id"), "answers", ["id"], unique=False)
    op.create_index(op.f("ix_answers_question_id"), "answers", ["question_id"], unique=False)
    op.create_index(op.f("ix_answers_title"), "answers", ["title"], unique=False)
    op.create_index(op.f("ix_answers_user_id"), "answers", ["user_id"], unique=False)
    op.create_table(
        "exercises",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("response", sa.TEXT(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("exercise_type", sa.String(length=128), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_exercises_id"), "exercises", ["id"], unique=False)
    op.create_index(op.f("ix_exercises_user_id"), "exercises", ["user_id"], unique=False)
    op.create_table(
        "files",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("file_name", sa.String(length=256), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_files_file_name"), "files", ["file_name"], unique=False)
    op.create_index(op.f("ix_files_id"), "files", ["id"], unique=False)
    op.create_index(op.f("ix_files_user_id"), "files", ["user_id"], unique=False)
    op.create_table(
        "notes",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=256), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_notes_id"), "notes", ["id"], unique=False)
    op.create_index(op.f("ix_notes_title"), "notes", ["title"], unique=False)
    op.create_index(op.f("ix_notes_user_id"), "notes", ["user_id"], unique=False)
    op.create_table(
        "outputs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("title", sa.String(length=100), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("output", sa.TEXT(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_outputs_id"), "outputs", ["id"], unique=False)
    op.create_index(op.f("ix_outputs_user_id"), "outputs", ["user_id"], unique=False)
    op.create_table(
        "exercise_file",
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
        ),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["files.id"],
        ),
        sa.PrimaryKeyConstraint("exercise_id", "file_id"),
    )
    op.create_table(
        "exercise_user_answers",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("exercise_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("answer", sa.TEXT(), nullable=False),
        sa.Column("scoring_results", sa.TEXT(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["exercise_id"],
            ["exercises.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_exercise_user_answers_exercise_id"),
        "exercise_user_answers",
        ["exercise_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_exercise_user_answers_id"), "exercise_user_answers", ["id"], unique=False
    )
    op.create_index(
        op.f("ix_exercise_user_answers_user_id"), "exercise_user_answers", ["user_id"], unique=False
    )
    op.create_table(
        "output_file",
        sa.Column("output_id", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["file_id"],
            ["files.id"],
        ),
        sa.ForeignKeyConstraint(
            ["output_id"],
            ["outputs.id"],
        ),
        sa.PrimaryKeyConstraint("output_id", "file_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("output_file")
    op.drop_index(op.f("ix_exercise_user_answers_user_id"), table_name="exercise_user_answers")
    op.drop_index(op.f("ix_exercise_user_answers_id"), table_name="exercise_user_answers")
    op.drop_index(op.f("ix_exercise_user_answers_exercise_id"), table_name="exercise_user_answers")
    op.drop_table("exercise_user_answers")
    op.drop_table("exercise_file")
    op.drop_index(op.f("ix_outputs_user_id"), table_name="outputs")
    op.drop_index(op.f("ix_outputs_id"), table_name="outputs")
    op.drop_table("outputs")
    op.drop_index(op.f("ix_notes_user_id"), table_name="notes")
    op.drop_index(op.f("ix_notes_title"), table_name="notes")
    op.drop_index(op.f("ix_notes_id"), table_name="notes")
    op.drop_table("notes")
    op.drop_index(op.f("ix_files_user_id"), table_name="files")
    op.drop_index(op.f("ix_files_id"), table_name="files")
    op.drop_index(op.f("ix_files_file_name"), table_name="files")
    op.drop_table("files")
    op.drop_index(op.f("ix_exercises_user_id"), table_name="exercises")
    op.drop_index(op.f("ix_exercises_id"), table_name="exercises")
    op.drop_table("exercises")
    op.drop_index(op.f("ix_answers_user_id"), table_name="answers")
    op.drop_index(op.f("ix_answers_title"), table_name="answers")
    op.drop_index(op.f("ix_answers_question_id"), table_name="answers")
    op.drop_index(op.f("ix_answers_id"), table_name="answers")
    op.drop_table("answers")
    # ### end Alembic commands ###
