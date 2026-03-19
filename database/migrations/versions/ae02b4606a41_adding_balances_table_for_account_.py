"""adding balances table for account monitoring

Revision ID: ae02b4606a41
Revises: 70dce8c50c36
Create Date: 2026-01-30 17:07:26.539894

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ae02b4606a41"
down_revision: Union[str, None] = "70dce8c50c36"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "acc_comp_monitoring_balance_history",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("account_address", sa.String(), nullable=False),
        sa.Column("resource_address", sa.String(), nullable=False),
        sa.Column("resource_name", sa.String(), nullable=True),
        sa.Column("balance", sa.Float(), nullable=False),
        sa.Column("previous_balance", sa.Float(), nullable=True),
        sa.Column("balance_change", sa.Float(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("acc_comp_monitoring_balance_history")
