from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas.validadores import rechazar_null


TipoMantenimiento = Literal[
    "Preventivo",
    "Predictivo",
    "Correctivo"
]


class MantenimientoCreate(BaseModel):
    equipo_id: int = Field(gt=0)
    falla_id: int | None = Field(default=None, gt=0)
    fecha: date
    tipo_mantenimiento: TipoMantenimiento
    # Duración en minutos.
    duracion_mantenimiento: int | None = Field(default=None, gt=0)
    descripcion: str | None = None
    resultado: str | None = None


class MantenimientoUpdate(BaseModel):
    falla_id: int | None = Field(default=None, gt=0)
    fecha: date | None = None
    tipo_mantenimiento: TipoMantenimiento | None = None
    duracion_mantenimiento: int | None = Field(default=None, gt=0)
    descripcion: str | None = None
    resultado: str | None = None

    # Los campos obligatorios pueden omitirse, pero no enviarse como null.
    @field_validator("fecha", "tipo_mantenimiento")
    @classmethod
    def validar_no_nulo(cls, valor):
        return rechazar_null(valor)


class MantenimientoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipo_id: int
    falla_id: int | None = None
    fecha: date
    tipo_mantenimiento: str
    duracion_mantenimiento: int | None = None
    descripcion: str | None = None
    resultado: str | None = None
    tecnico_ids: list[int]
