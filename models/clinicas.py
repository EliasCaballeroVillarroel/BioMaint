from __future__ import annotations

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base


class Clinica(Base):
    __tablename__ = "clinicas"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    direccion: Mapped[str | None] = mapped_column(String(200))

    ubicaciones: Mapped[list["Ubicacion"]] = relationship(
        back_populates="clinica"
    )
