from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas.validadores import rechazar_null


class ClinicaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    direccion: str | None = Field(default=None, max_length=200)


class ClinicaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    direccion: str | None = Field(default=None, max_length=200)

    # El nombre puede omitirse, pero no enviarse como null.
    @field_validator("nombre")
    @classmethod
    def validar_no_nulo(cls, valor):
        return rechazar_null(valor)


class ClinicaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    direccion: str | None = None
    activa: bool
