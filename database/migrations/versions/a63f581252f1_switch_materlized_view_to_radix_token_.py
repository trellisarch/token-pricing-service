"""switch materlized view to radix_token_prices_latest

Revision ID: a63f581252f1
Revises: dfe22591c380
Create Date: 2025-02-24 08:56:10.172979

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a63f581252f1"
down_revision: Union[str, None] = "dfe22591c380"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS latest_token_prices;
        CREATE MATERIALIZED VIEW latest_token_prices AS
        SELECT
            tp.id,
            tp.resource_address,
            tp.usd_price,
            tp.last_updated_at,
            t.allowlist
        FROM
            radix_token_prices_latest tp
        JOIN (
            SELECT
                resource_address,
                MAX(last_updated_at) as last_updated_at,
                MAX(id) as max_id -- tie-breaking condition
            FROM
                radix_token_prices_latest
            GROUP BY
                resource_address
        ) latest ON tp.resource_address = latest.resource_address AND tp.last_updated_at = latest.last_updated_at AND tp.id = latest.max_id
        JOIN radix_tokens t ON tp.resource_address = t.resource_address
        WHERE
            t.allowlist = TRUE;
    """)


def downgrade() -> None:
    op.execute("""
        DROP MATERIALIZED VIEW IF EXISTS latest_token_prices;
        CREATE MATERIALIZED VIEW latest_token_prices AS
        SELECT
            tp.id,
            tp.resource_address,
            tp.usd_price,
            tp.last_updated_at,
            t.allowlist
        FROM
            radix_token_prices tp
        JOIN (
            SELECT
                resource_address,
                MAX(last_updated_at) as last_updated_at,
                MAX(id) as max_id -- tie-breaking condition
            FROM
                radix_token_prices
            GROUP BY
                resource_address
        ) latest ON tp.resource_address = latest.resource_address AND tp.last_updated_at = latest.last_updated_at AND tp.id = latest.max_id
        JOIN radix_tokens t ON tp.resource_address = t.resource_address
        WHERE
            t.allowlist = TRUE;
    """)
