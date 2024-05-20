"""c9 lsu price

Revision ID: 0e72657c0037
Revises: 153902979829
Create Date: 2024-05-20 15:47:04.238137

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0e72657c0037"
down_revision: Union[str, None] = "153902979829"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "c9_lsu_price",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("price", sa.Float, nullable=False),
        sa.Column("source_address", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("c9_lsu_price")
