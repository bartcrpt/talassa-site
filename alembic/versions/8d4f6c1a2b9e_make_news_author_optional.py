"""make news author optional

Revision ID: 8d4f6c1a2b9e
Revises: 71d4adf7e2c3
Create Date: 2026-03-09 12:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '8d4f6c1a2b9e'
down_revision: Union[str, Sequence[str], None] = '71d4adf7e2c3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('news', 'author_id', existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    op.alter_column('news', 'author_id', existing_type=sa.Integer(), nullable=False)
