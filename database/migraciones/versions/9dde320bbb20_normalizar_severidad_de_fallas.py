"""normalizar severidad de fallas

Revision ID: 9dde320bbb20
Revises: deac1ad047fe
Create Date: 2026-10-24 16:21:56.082800

Migración de datos: la severidad pasa a ser una lista cerrada
(schemas/estados.py:SeveridadFalla) y los valores existentes se
llevan a minúsculas y sin tilde (ALTA -> alta, CRÍTICA -> critica).

El downgrade no es el inverso exacto: vuelve a mayúsculas, pero no
restaura la tilde (critica -> CRITICA) ni los espacios quitados.
"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9dde320bbb20"
down_revision: str | Sequence[str] | None = "deac1ad047fe"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "UPDATE fallas SET severidad = LOWER(TRIM(severidad)) "
        "WHERE severidad IS NOT NULL"
    )
    op.execute("UPDATE fallas SET severidad = 'critica' WHERE severidad = 'crítica'")


def downgrade() -> None:
    """Downgrade schema."""
    # El formato original era en mayúsculas (datos de ejemplo).
    op.execute(
        "UPDATE fallas SET severidad = UPPER(severidad) WHERE severidad IS NOT NULL"
    )
