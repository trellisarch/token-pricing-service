"""add npm metrics

Revision ID: 8d84997aec5f
Revises: 707a6defd36f
Create Date: 2024-06-20 12:08:21.958529

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "8d84997aec5f"
down_revision: Union[str, None] = "707a6defd36f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "npm_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("package_name", sa.String(), nullable=False),
        sa.Column("downloads", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("npm_metrics")
