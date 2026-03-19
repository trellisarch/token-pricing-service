"""Make columns nullable in google_play_store_performance

Revision ID: a101e3837f88
Revises: 8d84997aec5f
Create Date: 2024-09-30 18:03:08.368911

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a101e3837f88"
down_revision: Union[str, None] = "8d84997aec5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Make columns nullable
    op.alter_column(
        "google_play_store_performance",
        "store_listing_visitors",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.alter_column(
        "google_play_store_performance",
        "store_listing_conversion_rate",
        existing_type=sa.Integer(),
        nullable=True,
    )

    op.alter_column(
        "google_play_store_performance",
        "store_listing_acquisitions",
        existing_type=sa.Integer(),
        nullable=True,
    )


def downgrade():
    # Revert columns to non-nullable
    op.alter_column(
        "google_play_store_performance",
        "store_listing_visitors",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "google_play_store_performance",
        "store_listing_conversion_rate",
        existing_type=sa.Integer(),
        nullable=False,
    )

    op.alter_column(
        "google_play_store_performance",
        "store_listing_acquisitions",
        existing_type=sa.Integer(),
        nullable=False,
    )
