"""create links table

Revision ID: 25f00952c2d6
Revises:
Create Date: 2026-09-29 13:53:02.960180

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "25f00952c2d6"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "links",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=16), nullable=False),
        sa.Column("target_url", sa.Text(), nullable=False),
        sa.Column("clicks", sa.Integer(), server_default="0", nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_index("ix_links_code", "links", ["code"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_links_code", table_name="links")
    op.drop_table("links")
