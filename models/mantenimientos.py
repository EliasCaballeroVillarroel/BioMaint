from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.equipos import Equipo
    from models.fallas import Falla
    from models.tecnicos import Tecnico


class Mantenimiento(Base):
    __tablename__ = "mantenimientos"

    id: Mapped[int] = mapped_column(primary_key=True)

    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"), nullable=False)

    falla_id: Mapped[int | None] = mapped_column(ForeignKey("fallas.id"), nullable=True)

    fecha: Mapped[date] = mapped_column(Date, nullable=False)

    tipo_mantenimiento: Mapped[str] = mapped_column(String(30), nullable=False)

    duracion_mantenimiento: Mapped[int | None] = mapped_column(Integer)

    descripcion: Mapped[str | None] = mapped_column(Text)
    resultado: Mapped[str | None] = mapped_column(Text)

    equipo: Mapped[Equipo] = relationship(back_populates="mantenimientos")

    falla: Mapped[Falla | None] = relationship(back_populates="mantenimientos")
    tecnicos: Mapped[list[Tecnico]] = relationship(
        secondary="mantenimiento_tecnicos", back_populates="mantenimientos"
    )

    @property
    def finalizado(self) -> bool:
        # Un mantenimiento con resultado cargado ya ocurrió: es historial.
        return bool(self.resultado and self.resultado.strip())

    @property
    def tecnico_ids(self) -> list[int]:
        return sorted(tecnico.id for tecnico in self.tecnicos)
