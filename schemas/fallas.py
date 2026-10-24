
from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class FallaCreate(BaseModel):
    equipo_id: int = Field(gt=0)
    tipo_falla: str = Field(min_length=1, max_length=100)
    descripcion_falla: str | None = None
    fecha_falla: date
    fecha_resolucion: date | None = None
    severidad: str | None = Field(default=None, max_length=50)

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
    tipo_falla: str | None = Field(
        default=None, min_length=1, max_length=100
    )
    descripcion_falla: str | None = None
    fecha_falla: date | None = None
    fecha_resolucion: date | None = None
    severidad: str | None = Field(default=None, max_length=50)

    @model_validator(mode="after")
    def validar_fechas(self):
        if (
            self.fecha_falla is not None
            and self.fecha_resolucion is not None
            and self.fecha_resolucion < self.fecha_falla
        ):
            raise ValueError(
                "La fecha de resolución no puede ser anterior a la fecha de la falla."
            )
        return self


class FallaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipo_id: int
    tipo_falla: str
    descripcion_falla: str | None = None
    fecha_falla: date
    fecha_resolucion: date | None = None
    severidad: str | None = None
