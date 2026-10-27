from __future__ import annotations

from sqlalchemy import Boolean, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.ubicaciones import Ubicacion


class Clinica(Base):
    __tablename__ = "clinicas"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    direccion: Mapped[str | None] = mapped_column(String(200))

    # Baja lógica: una clínica inactiva se conserva en la base.
    activa: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    ubicaciones: Mapped[list["Ubicacion"]] = relationship(back_populates="clinica")
