"""Add exercise_file association table

Revision ID: 1f25e371eadc
Revises: 93f95e7aa12b
Create Date: 2024-11-02 12:09:36.382455

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1f25e371eadc"
down_revision: Union[str, None] = "93f95e7aa12b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
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
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("exercise_file")
    # ### end Alembic commands ###
