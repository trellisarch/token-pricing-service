"""oracle tokens tables

Revision ID: 74af06621960
Revises: fa409f33202a
Create Date: 2024-01-29 16:09:44.630635

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '74af06621960'
down_revision: Union[str, None] = 'fa409f33202a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "oracle_token_prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pair", sa.String(), nullable=False),
        sa.Column("quote", sa.String(), nullable=False),
        sa.Column("quote_source", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("oracle_token_prices")
