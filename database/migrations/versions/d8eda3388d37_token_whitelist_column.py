"""token_whitelist_column

Revision ID: d8eda3388d37
Revises: b0ea0867a2df
Create Date: 2024-04-03 10:37:51.878404

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "d8eda3388d37"
down_revision: Union[str, None] = "b0ea0867a2df"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column("radix_tokens", sa.Column("whitelisted", sa.Boolean(), nullable=True))
    op.execute("UPDATE radix_tokens SET whitelisted = TRUE")


def downgrade():
    op.drop_column("radix_tokens", "whitelisted")
