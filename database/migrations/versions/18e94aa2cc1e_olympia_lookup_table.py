"""olympia_lookup_table

Revision ID: 18e94aa2cc1e
Revises: a3e526d3066f
Create Date: 2024-01-16 14:48:17.738778

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '18e94aa2cc1e'
down_revision: Union[str, None] = 'a3e526d3066f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "olympia_babylon_addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("olympia_address", sa.String(), nullable=False),
        sa.Column("babylon_address", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table(table_name="olympia_babylon_addresses")
