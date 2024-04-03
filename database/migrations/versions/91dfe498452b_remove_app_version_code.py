"""remove_app_version_code

Revision ID: 91dfe498452b
Revises: d8eda3388d37
Create Date: 2024-04-03 16:34:17.564056

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "91dfe498452b"
down_revision: Union[str, None] = "d8eda3388d37"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("google_play_store_performance", "app_version_code")


def downgrade() -> None:
    op.add_column("google_play_store_performance", "app_version_code")
