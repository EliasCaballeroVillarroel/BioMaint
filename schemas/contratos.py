from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from schemas.validadores import rechazar_null


# Calculado a partir de las fechas (ver models/contratos.py).
EstadoContrato = Literal[
    "Activo",
    "Vencido",
    "Cancelado",
    "Pendiente",
]


class ContratoCreate(BaseModel):
    equipo_id: int = Field(gt=0)
    tipo_contrato: str = Field(min_length=1, max_length=100)
    empresa: str | None = Field(default=None, max_length=100)
    fecha_inicio: date
    fecha_fin: date | None = None

    @model_validator(mode="after")
    def validar_fechas(self):
        if self.fecha_fin is not None and self.fecha_fin < self.fecha_inicio:
            raise ValueError(
                "La fecha de fin no puede ser anterior a la fecha de inicio."
            )
        return self


class ContratoUpdate(BaseModel):
    tipo_contrato: str | None = Field(default=None, min_length=1, max_length=100)
    empresa: str | None = Field(default=None, max_length=100)
    fecha_inicio: date | None = None
    fecha_fin: date | None = None

    # Los campos obligatorios pueden omitirse, pero no enviarse como null.
    @field_validator("tipo_contrato", "fecha_inicio")
    @classmethod
    def validar_no_nulo(cls, valor):
        return rechazar_null(valor)

    # El orden de las fechas se valida en el router, contra los
    # valores que ya tiene el contrato.


class ContratoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipo_id: int
    tipo_contrato: str
    empresa: str | None = None
    fecha_inicio: date
    fecha_fin: date | None = None
    estado: EstadoContrato
