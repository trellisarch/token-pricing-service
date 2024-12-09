"""burn properties nulleables

Revision ID: 8ce7cc6d9db1
Revises: a101e3837f88
Create Date: 2024-12-09 11:01:32.562374

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8ce7cc6d9db1"
down_revision: Union[str, None] = "a101e3837f88"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():

    # Make columns nullable
    op.alter_column(
        "network",
        "hourly_burnt_amount",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "daily_burnt_amount",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "weekly_burnt_amount",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "monthly_burnt_amount",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "annually_burnt_amount",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "price",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "current_block",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "max_supply",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "burnt_amount",
        existing_type=sa.Float(),
        nullable=True,
    )

    op.alter_column(
        "network",
        "remaining_supply",
        existing_type=sa.Float(),
        nullable=True,
    )

    pass


def downgrade() -> None:

    # Make columns nullable
    op.alter_column(
        "network",
        "hourly_burnt_amount",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "daily_burnt_amount",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "weekly_burnt_amount",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "monthly_burnt_amount",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "annually_burnt_amount",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "price",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "current_block",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "max_supply",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "burnt_amount",
        existing_type=sa.Float(),
        nullable=False,
    )

    op.alter_column(
        "network",
        "remaining_supply",
        existing_type=sa.Float(),
        nullable=False,
    )

    pass
