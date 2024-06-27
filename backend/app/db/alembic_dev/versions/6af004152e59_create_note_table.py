"""create note table

Revision ID: 6af004152e59
Revises: 8b4935a1163c
Create Date: 2024-06-22 15:49:44.140835

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6af004152e59'
down_revision: Union[str, None] = '8b4935a1163c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=256), nullable=False),
    sa.Column('content', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notes_id'), 'notes', ['id'], unique=False)
    op.create_index(op.f('ix_notes_title'), 'notes', ['title'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notes_title'), table_name='notes')
    op.drop_index(op.f('ix_notes_id'), table_name='notes')
    op.drop_table('notes')
    # ### end Alembic commands ###