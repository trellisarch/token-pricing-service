"""Fix network reddit telegram and add tokens table.py

Revision ID: 399f387cfeba
Revises: a5361c1407f1
Create Date: 2024-03-12 13:45:28.694909

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "399f387cfeba"
down_revision: Union[str, None] = "a5361c1407f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Adding new columns to reddit_subreddit
    op.add_column(
        "reddit_subreddit", sa.Column("unique_pageviews", sa.Integer(), nullable=True)
    )
    op.add_column(
        "reddit_subreddit", sa.Column("total_pageviews", sa.Integer(), nullable=True)
    )
    op.add_column(
        "reddit_subreddit", sa.Column("subscribers", sa.Integer(), nullable=True)
    )

    # Renaming columns in telegram
    op.alter_column("telegram", "week_messages_total", new_column_name="messages_total")
    op.alter_column(
        "telegram", "week_new_users_total", new_column_name="new_users_total"
    )
    op.alter_column(
        "telegram", "week_left_users_total", new_column_name="left_users_total"
    )
    op.alter_column(
        "telegram", "week_active_users_total", new_column_name="active_users_total"
    )

    # Deleting columns from network table
    op.drop_column("network", "xrd_market_cap_usd")
    op.drop_column("network", "xrd_total_volume_usd")
    op.drop_column("network", "exrd_market_cap_usd")
    op.drop_column("network", "exrd_total_volume_usd")

    # Creating new tokens table
    op.create_table(
        "tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_id", sa.String(), nullable=False),
        sa.Column("symbol", sa.String(), nullable=False),
        sa.Column("market_cap_usd", sa.Float(), nullable=False),
        sa.Column("total_volume_usd", sa.Float(), nullable=False),
        sa.Column("sentiment_votes_up_percentage", sa.Float(), nullable=False),
        sa.Column("sentiment_votes_down_percentage", sa.Float(), nullable=False),
        sa.Column("watchlist_portfolio_users", sa.Float(), nullable=False),
        sa.Column("market_cap_rank", sa.Float(), nullable=False),
        sa.Column("current_price", sa.Float(), nullable=False),
        sa.Column("total_value_locked_usd", sa.Float(), nullable=False),
        sa.Column("total_value_locked_btc", sa.Float(), nullable=False),
        sa.Column("mcap_to_tvl_ratio", sa.Float(), nullable=False),
        sa.Column("fdv_to_tvl_ratio", sa.Float(), nullable=False),
        sa.Column("ath", sa.Float(), nullable=False),
        sa.Column("ath_change_percentage", sa.Float(), nullable=False),
        sa.Column("ath_date", sa.DateTime(), nullable=False),
        sa.Column("atl", sa.Float(), nullable=False),
        sa.Column("atl_change_percentage", sa.Float(), nullable=False),
        sa.Column("atl_date", sa.DateTime(), nullable=False),
        sa.Column("fully_diluted_valuation", sa.Float(), nullable=False),
        sa.Column("market_cap_fdv_ratio", sa.Float(), nullable=False),
        sa.Column("high_24h", sa.Float(), nullable=False),
        sa.Column("low_24h", sa.Float(), nullable=False),
        sa.Column("circulating_supply", sa.Float(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    # Removing added columns from reddit_subreddit
    op.drop_column("reddit_subreddit", "unique_pageviews")
    op.drop_column("reddit_subreddit", "total_pageviews")
    op.drop_column("reddit_subreddit", "subscribers")

    # Reverting column name changes in telegram
    op.alter_column("telegram", "messages_total", new_column_name="week_messages_total")
    op.alter_column(
        "telegram", "new_users_total", new_column_name="week_new_users_total"
    )
    op.alter_column(
        "telegram", "left_users_total", new_column_name="week_left_users_total"
    )
    op.alter_column(
        "telegram", "active_users_total", new_column_name="week_active_users_total"
    )

    # Adding columns back to network table
    op.add_column(
        "network", sa.Column("xrd_market_cap_usd", sa.Float(), nullable=False)
    )
    op.add_column(
        "network", sa.Column("xrd_total_volume_usd", sa.Float(), nullable=False)
    )
    op.add_column(
        "network", sa.Column("exrd_market_cap_usd", sa.Float(), nullable=False)
    )
    op.add_column(
        "network", sa.Column("exrd_total_volume_usd", sa.Float(), nullable=False)
    )

    # Dropping the tokens table
    op.drop_table("tokens")
