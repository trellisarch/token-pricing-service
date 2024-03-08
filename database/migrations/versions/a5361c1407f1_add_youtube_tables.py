"""Add youtube tables

Revision ID: a5361c1407f1
Revises: bb3ab9c2be89
Create Date: 2024-02-22 18:03:31.146494

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a5361c1407f1"
down_revision: Union[str, None] = "bb3ab9c2be89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "youtube",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account", sa.String(), nullable=False),
        sa.Column("total_views", sa.Integer(), nullable=True),
        sa.Column("average_watchtime", sa.Integer(), nullable=True),
        sa.Column("new_subs", sa.Integer(), nullable=True),
        sa.Column("lost_subs", sa.Integer(), nullable=True),
        sa.Column("estimated_minutes_watched", sa.Integer(), nullable=True),
        sa.Column("annotation_impressions", sa.Integer(), nullable=True),
        sa.Column("average_view_percentage", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("youtube")
