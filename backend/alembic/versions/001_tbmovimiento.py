"""tbmovimiento ledger

Revision ID: 001
Revises:
Create Date: 2026-07-14
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tbmovimiento",
        sa.Column("id_movimiento", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("id_tarjeta", sa.Integer(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("monto", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("saldo_anterior", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("saldo_nuevo", sa.DECIMAL(precision=10, scale=2), nullable=False),
        sa.Column("referencia", sa.String(length=80), nullable=True),
        sa.Column("creado_en", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id_movimiento"),
        sa.ForeignKeyConstraint(["id_tarjeta"], ["tbtarjeta_digital.id_tarjeta"]),
    )


def downgrade() -> None:
    op.drop_table("tbmovimiento")
