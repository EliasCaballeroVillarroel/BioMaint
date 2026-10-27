from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.equipos import Equipo
    from models.mantenimientos import Mantenimiento


class Falla(Base):
    __tablename__ = "fallas"

    id: Mapped[int] = mapped_column(primary_key=True)

    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"), nullable=False)

    tipo_falla: Mapped[str] = mapped_column(String(100), nullable=False)

    descripcion_falla: Mapped[str | None] = mapped_column(Text)

    fecha_falla: Mapped[date] = mapped_column(Date, nullable=False)

    fecha_resolucion: Mapped[date | None] = mapped_column(Date)

    severidad: Mapped[str | None] = mapped_column(String(50))

    equipo: Mapped[Equipo] = relationship(back_populates="fallas")
    mantenimientos: Mapped[list[Mantenimiento]] = relationship(back_populates="falla")

    @property
    def resuelta(self) -> bool:
        # Una falla está abierta hasta que se registra su resolución.
        return self.fecha_resolucion is not None
