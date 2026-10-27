"""estado de contratos calculado

Revision ID: 26d80ad4948d
Revises: 9dde320bbb20
Create Date: 2026-10-24 16:54:35.053369

El estado de un contrato pasa a calcularse a partir de sus fechas
(Pendiente / Activo / Vencido). Solo la cancelación se guarda, en la
columna nueva `cancelado`, que reemplaza a la columna `estado`.

El downgrade reconstruye el estado con la fecha del día en que se
ejecuta, así que Pendiente/Activo/Vencido pueden diferir de los
valores originales si pasó el tiempo.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "26d80ad4948d"
down_revision: str | Sequence[str] | None = "9dde320bbb20"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "contratos",
        sa.Column(
            "cancelado",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
    )
    # Conservar las cancelaciones; el resto del estado se deduce.
    op.execute("UPDATE contratos SET cancelado = TRUE WHERE estado = 'Cancelado'")
    op.drop_column("contratos", "estado")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column(
        "contratos",
        sa.Column(
            "estado",
            sa.String(length=30),
            server_default="Activo",
            nullable=False,
        ),
    )
    # Reconstruir el estado con la misma regla que models/contratos.py.
    op.execute(
        "UPDATE contratos SET estado = CASE "
        "WHEN cancelado THEN 'Cancelado' "
        "WHEN fecha_inicio > CURDATE() THEN 'Pendiente' "
        "WHEN fecha_fin IS NOT NULL AND fecha_fin < CURDATE() THEN 'Vencido' "
        "ELSE 'Activo' END"
    )
    op.alter_column(
        "contratos",
        "estado",
        existing_type=sa.String(length=30),
        server_default=None,
    )
    op.drop_column("contratos", "cancelado")
