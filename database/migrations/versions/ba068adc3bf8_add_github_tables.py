"""add github tables

Revision ID: ba068adc3bf8
Revises: 18e94aa2cc1e
Create Date: 2024-01-17 18:21:28.747318

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "ba068adc3bf8"
down_revision: Union[str, None] = "18e94aa2cc1e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "twitter",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account", sa.String(), nullable=False),
        sa.Column("followers_count", sa.Integer(), nullable=False),
        sa.Column("friends_count", sa.Integer(), nullable=False),
        sa.Column("statuses_count", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "telegram",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account", sa.String(), nullable=False),
        sa.Column("members_total", sa.Integer(), nullable=False),
        sa.Column("week_messages_total", sa.Integer(), nullable=False),
        sa.Column("week_new_users_total", sa.Integer(), nullable=False),
        sa.Column("week_left_users_total", sa.Integer(), nullable=False),
        sa.Column("week_active_users_total", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "github_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account", sa.String(), nullable=False),
        sa.Column("public_repos_total", sa.Integer(), nullable=False),
        sa.Column("followers_total", sa.Integer(), nullable=False),
        sa.Column("gists_total", sa.Integer(), nullable=False),
        sa.Column("following_total", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "github_repositories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("account", sa.String(), nullable=False),
        sa.Column("repository", sa.String(), nullable=False),
        sa.Column("commits", sa.Integer(), nullable=False),
        sa.Column("branches", sa.Integer(), nullable=False),
        sa.Column("pr_all", sa.Integer(), nullable=False),
        sa.Column("pr_open", sa.Integer(), nullable=False),
        sa.Column("pr_closed", sa.Integer(), nullable=False),
        sa.Column("issues_all", sa.Integer(), nullable=False),
        sa.Column("issues_open", sa.Integer(), nullable=False),
        sa.Column("issues_closed", sa.Integer(), nullable=False),
        sa.Column("contributors", sa.Integer(), nullable=False),
        sa.Column("releases", sa.Integer(), nullable=False),
        sa.Column("subscribers", sa.Integer(), nullable=False),
        sa.Column("tags", sa.Integer(), nullable=False),
        sa.Column("watchers", sa.Integer(), nullable=False),
        sa.Column("clones_traffic", sa.Integer(), nullable=False),
        sa.Column("clones_traffic_unique", sa.Integer(), nullable=False),
        sa.Column("views_traffic", sa.Integer(), nullable=False),
        sa.Column("views_traffic_unique", sa.Integer(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("twitter")
    op.drop_table("telegram")
    op.drop_table("github_accounts")
    op.drop_table("github_repositories")
