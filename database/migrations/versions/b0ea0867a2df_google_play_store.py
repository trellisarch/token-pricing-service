"""google_play_store

Revision ID: b0ea0867a2df
Revises: 43807e62a606
Create Date: 2024-04-02 16:04:14.222913

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "b0ea0867a2df"
down_revision: Union[str, None] = "43807e62a606"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "google_play_store_performance",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("package_name", sa.String, nullable=False),
        sa.Column("app_version_code", sa.String, nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("store_listing_acquisitions", sa.Integer, nullable=False),
        sa.Column("store_listing_visitors", sa.Integer, nullable=False),
        sa.Column("store_listing_conversion_rate", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "google_play_installs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("package_name", sa.String, nullable=False),
        sa.Column("app_version_code", sa.String, nullable=False),
        sa.Column("daily_device_installs", sa.Integer, nullable=True),
        sa.Column("daily_device_uninstalls", sa.Integer, nullable=True),
        sa.Column("daily_device_upgrades", sa.Integer, nullable=True),
        sa.Column("total_user_installs", sa.Integer, nullable=True),
        sa.Column("daily_user_installs", sa.Integer, nullable=True),
        sa.Column("daily_user_uninstalls", sa.Integer, nullable=True),
        sa.Column("active_device_installs", sa.Integer, nullable=True),
        sa.Column("install_events", sa.Integer, nullable=True),
        sa.Column("update_events", sa.Integer, nullable=True),
        sa.Column("uninstall_events", sa.Integer, nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "google_play_ratings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("package_name", sa.String, nullable=False),
        sa.Column("app_version_code", sa.String, nullable=False),
        sa.Column("daily_avg_rating", sa.Float, nullable=False),
        sa.Column("total_avg_rating", sa.Float, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("google_play_store_performance")
    op.drop_table("google_play_installs")
    op.drop_table("google_play_ratings")
