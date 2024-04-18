"""rename whitelist column

Revision ID: 153902979829
Revises: 91dfe498452b
Create Date: 2024-04-18 12:19:13.036879

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "153902979829"
down_revision: Union[str, None] = "91dfe498452b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "radix_tokens",
        "whitelisted",
        new_column_name="allowlist",
        existing_type=sa.Boolean,
    )


def downgrade() -> None:
    op.alter_column(
        "radix_tokens",
        "allowlist",
        new_column_name="whitelisted",
        existing_type=sa.Boolean,
    )
