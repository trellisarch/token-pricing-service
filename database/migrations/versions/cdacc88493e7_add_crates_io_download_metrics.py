"""add crates io download metrics

Revision ID: cdacc88493e7
Revises: b52d85dcea47
Create Date: 2024-07-01 13:52:42.583710

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "cdacc88493e7"
down_revision: Union[str, None] = "b52d85dcea47"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "crates_io_downloads",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("package", sa.String(), nullable=True),
        sa.Column("downloads", sa.Integer(), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_table("crates_io_downloads")
    # ### end Alembic commands ###
