"""transactions table

Revision ID: 5c4414c657ea
Revises: 399f387cfeba
Create Date: 2024-03-14 14:53:58.637064

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5c4414c657ea"
down_revision: Union[str, None] = "399f387cfeba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "oracle_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pair", sa.String(), nullable=False),
        sa.Column("quote", sa.Float, nullable=False),
        sa.Column("quote_source", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("transaction_id", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "oracle_source_prices",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pair", sa.String(), nullable=False),
        sa.Column("quote", sa.Float, nullable=False),
        sa.Column("quote_source", sa.String(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.Column("last_updated", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("oracle_transactions")
    op.drop_table("oracle_source_prices")
