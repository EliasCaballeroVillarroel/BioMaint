from __future__ import annotations

from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Contrato(Base):
    __tablename__ = "contratos"

    id: Mapped[int] = mapped_column(primary_key=True)

    equipo_id: Mapped[int] = mapped_column(
        ForeignKey("equipos.id"),
        nullable=False
    )

    tipo_contrato: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    empresa: Mapped[str | None] = mapped_column(String(100))

    fecha_inicio: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    fecha_fin: Mapped[date | None] = mapped_column(Date)

    estado: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    equipo: Mapped["Equipo"] = relationship(
        back_populates="contratos"
    )
