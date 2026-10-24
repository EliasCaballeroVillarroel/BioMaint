from __future__ import annotations
from sqlalchemy import String, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.base import Base


class Equipo(Base): #Creamos una clase que va representar a equipos 
    __tablename__ = "equipos" #Definimos la tabla a representar 

    id: Mapped[int] = mapped_column(primary_key=True) #Mapped int represneta que es un valor entero que sql va a mapear en una columna 
    ubicacion_id: Mapped[int] = mapped_column(ForeignKey("ubicaciones.id"),nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)
    tipo: Mapped[str | None] = mapped_column(String(100)) #str | None implica que puede ser un str o None 
    modelo: Mapped[str | None] = mapped_column(String(100))
    marca: Mapped[str | None] = mapped_column(String(100))

    numero_serie: Mapped[str | None] = mapped_column(
        String(100),
        unique=True
    )

    fecha_adquisicion: Mapped[Date | None] = mapped_column(Date)
    fecha_instalacion: Mapped[Date | None] = mapped_column(Date)

    estado_actual: Mapped[str] = mapped_column(
        String(30),
        nullable=False
    )

    ubicacion: Mapped["Ubicacion"] = relationship(
        back_populates="equipos"
    )
    fallas: Mapped[list["Falla"]] = relationship(
    back_populates="equipo"
    )
    mantenimientos: Mapped[list["Mantenimiento"]] = relationship(
    back_populates="equipo"
    )
    contratos: Mapped[list["Contrato"]] = relationship(
    back_populates="equipo"
    )

    @property
    def dado_de_baja(self) -> bool:
        return self.estado_actual == "dado_de_baja"

    @property
    def ubicacion_activa(self) -> bool:
        # Marca calculada: False si la clínica del equipo está dada de baja.
        # El equipo sigue operativo y se puede trasladar a otra ubicación.
        return self.ubicacion.activa