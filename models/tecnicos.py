from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base

if TYPE_CHECKING:
    from models.mantenimientos import Mantenimiento


class Tecnico(Base):
    __tablename__ = "tecnicos"

    id: Mapped[int] = mapped_column(primary_key=True)

    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    apellido: Mapped[str] = mapped_column(String(100), nullable=False)

    empresa: Mapped[str | None] = mapped_column(String(100))

    mantenimientos: Mapped[list[Mantenimiento]] = relationship(
        secondary="mantenimiento_tecnicos", back_populates="tecnicos"
    )
