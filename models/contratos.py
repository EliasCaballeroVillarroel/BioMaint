from __future__ import annotations

from datetime import date

from sqlalchemy import Boolean, Date, ForeignKey, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from models.equipos import Equipo


class Contrato(Base):
    __tablename__ = "contratos"

    id: Mapped[int] = mapped_column(primary_key=True)

    equipo_id: Mapped[int] = mapped_column(ForeignKey("equipos.id"), nullable=False)

    tipo_contrato: Mapped[str] = mapped_column(String(100), nullable=False)

    empresa: Mapped[str | None] = mapped_column(String(100))

    fecha_inicio: Mapped[date] = mapped_column(Date, nullable=False)

    fecha_fin: Mapped[date | None] = mapped_column(Date)

    # El estado se calcula a partir de las fechas; solo la
    # cancelación se registra a mano (POST /contratos/{id}/cancelar).
    cancelado: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=false()
    )

    equipo: Mapped["Equipo"] = relationship(back_populates="contratos")

    @property
    def estado(self) -> str:
        if self.cancelado:
            return "Cancelado"

        hoy = date.today()

        if self.fecha_inicio > hoy:
            return "Pendiente"

        if self.fecha_fin is not None and self.fecha_fin < hoy:
            return "Vencido"

        return "Activo"
