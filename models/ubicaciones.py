from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.clinicas import Clinica
    from models.equipos import Equipo


class Ubicacion(Base):
    __tablename__ = "ubicaciones"

    id: Mapped[int] = mapped_column(primary_key=True)

    clinica_id: Mapped[int] = mapped_column(ForeignKey("clinicas.id"), nullable=False)

    servicio: Mapped[str | None] = mapped_column(String(100))
    sector: Mapped[str | None] = mapped_column(String(100))
    piso: Mapped[str | None] = mapped_column(String(20))
    sala: Mapped[str | None] = mapped_column(String(50))

    # Se inactiva en cascada al dar de baja su clínica.
    activa: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )

    equipos: Mapped[list[Equipo]] = relationship(back_populates="ubicacion")
    clinica: Mapped[Clinica] = relationship(back_populates="ubicaciones")
