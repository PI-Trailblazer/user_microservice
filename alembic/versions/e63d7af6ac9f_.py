"""empty message

Revision ID: e63d7af6ac9f
Revises: 
Create Date: 2024-03-26 02:47:58.545723

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.core.config import settings


# revision identifiers, used by Alembic.
revision: str = "e63d7af6ac9f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    scope_enum = postgresql.ENUM(
        "ADMIN",
        "PROVIDER",
        "USER",
        name="scope_enum",
        schema=settings.SCHEMA_NAME,
        inherit_schema=True,
        create_type=False,
    )
    scope_enum.create(op.get_bind(), checkfirst=True)
    op.create_table(
        "user",
        sa.Column("id", sa.String(length=128), nullable=False),
        sa.Column("email", sa.String(length=64), nullable=False),
        sa.Column("f_name", sa.String(length=32), nullable=False),
        sa.Column("l_name", sa.String(length=32), nullable=False),
        sa.Column("phone_number", sa.String(length=14), nullable=True),
        sa.Column("roles", postgresql.ARRAY(scope_enum), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=False),
        sa.Column("tags", sa.ARRAY(sa.Text()), nullable=False),
        sa.Column("image", sa.String(length=2048), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        schema=settings.SCHEMA_NAME,
    )
    op.create_index(
        op.f("ix_user_email"),
        "user",
        ["email"],
        unique=True,
        schema=settings.SCHEMA_NAME,
    )
    op.create_table(
        "device_login",
        sa.Column("user_id", sa.String(length=128), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("refreshed_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["nei.user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "session_id"),
        schema=settings.SCHEMA_NAME,
    )
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("device_login", schema=settings.SCHEMA_NAME)
    op.drop_index(op.f("ix_user_email"), table_name="user", schema=settings.SCHEMA_NAME)
    op.drop_table("user", schema=settings.SCHEMA_NAME)
    scopes_enum = postgresql.ENUM(
        name="scope_enum",
        schema=settings.SCHEMA_NAME,
        inherit_schema=True,
        create_type=False,
    )
    scopes_enum.drop(op.get_bind(), checkfirst=False)
    pass
    # ### end Alembic commands ###
