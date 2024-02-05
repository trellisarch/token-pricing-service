"""add reddit tables

Revision ID: bb3ab9c2be89
Revises: 74af06621960
Create Date: 2024-01-29 19:46:37.246177

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "bb3ab9c2be89"
down_revision: Union[str, None] = "74af06621960"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "reddit_subreddit",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account", sa.String(), nullable=True),
        sa.Column("subscribers_count", sa.Integer(), nullable=True),
        sa.Column("active_user_count", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "reddit_redditor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account", sa.String(), nullable=True),
        sa.Column("comment_karma", sa.Integer(), nullable=True),
        sa.Column("link_karma", sa.Integer(), nullable=True),
        sa.Column("total_karma", sa.Integer(), nullable=True),
        sa.Column("trophy_count", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("reddit_subreddit")
    op.drop_table("reddit_redditor")
