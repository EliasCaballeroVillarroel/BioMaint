from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from schemas.estados import SeveridadFalla
from schemas.validadores import rechazar_fecha_futura, rechazar_null


class FallaCreate(BaseModel):
    equipo_id: int = Field(gt=0)
    tipo_falla: str = Field(min_length=1, max_length=100)
    descripcion_falla: str | None = None
    fecha_falla: date
    fecha_resolucion: date | None = None
    severidad: SeveridadFalla | None = None

    @field_validator("fecha_falla", "fecha_resolucion")
    @classmethod
    def validar_fecha(cls, fecha):
        return rechazar_fecha_futura(fecha)

    @model_validator(mode="after")
    def validar_fechas(self):
        if (
            self.fecha_resolucion is not None
            and self.fecha_resolucion < self.fecha_falla
        ):
            raise ValueError(
                "La fecha de resolución no puede ser anterior a la fecha de la falla."
            )
        return self


class FallaUpdate(BaseModel):
    tipo_falla: str | None = Field(default=None, min_length=1, max_length=100)
    descripcion_falla: str | None = None
    fecha_falla: date | None = None
    fecha_resolucion: date | None = None
    severidad: SeveridadFalla | None = None

    # Los campos obligatorios pueden omitirse, pero no enviarse como null.
    @field_validator("tipo_falla", "fecha_falla")
    @classmethod
    def validar_no_nulo(cls, valor):
        return rechazar_null(valor)

    @field_validator("fecha_falla", "fecha_resolucion")
    @classmethod
    def validar_fecha(cls, fecha):
        return rechazar_fecha_futura(fecha)

    # El orden de las fechas se valida en el CRUD, contra los
    # valores que ya tiene la falla.


class FallaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipo_id: int
    tipo_falla: str
    descripcion_falla: str | None = None
    fecha_falla: date
    fecha_resolucion: date | None = None
    severidad: str | None = None
    resuelta: bool
