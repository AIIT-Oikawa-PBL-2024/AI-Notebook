"""add create/update columns

Revision ID: ee7ece65c406
Revises: 6af004152e59
Create Date: 2024-06-24 06:00:19.114578

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ee7ece65c406'
down_revision: Union[str, None] = '6af004152e59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('notes', sa.Column('created_at', sa.DateTime(), nullable=False))
    op.add_column('notes', sa.Column('updated_at', sa.DateTime(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('notes', 'updated_at')
    op.drop_column('notes', 'created_at')
    # ### end Alembic commands ###
