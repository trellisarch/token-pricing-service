"""transactions commited table

Revision ID: 04992dfa3cc8
Revises: 5c4414c657ea
Create Date: 2024-03-20 15:29:37.565207

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "04992dfa3cc8"
down_revision: Union[str, None] = "5c4414c657ea"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "committed_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("transaction_intent_hash", sa.String(), nullable=False),
        sa.Column("pairs_updated", sa.Integer, nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("committed_transactions")
