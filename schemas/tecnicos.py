from pydantic import BaseModel, ConfigDict, Field, field_validator
from schemas.validadores import rechazar_null


class TecnicoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    apellido: str = Field(min_length=1, max_length=100)
    empresa: str | None = Field(default=None, max_length=100)


class TecnicoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    apellido: str | None = Field(default=None, min_length=1, max_length=100)
    empresa: str | None = Field(default=None, max_length=100)

    # Los campos obligatorios pueden omitirse, pero no enviarse como null.
    @field_validator("nombre", "apellido")
    @classmethod
    def validar_no_nulo(cls, valor):
        return rechazar_null(valor)


class TecnicoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    apellido: str
    empresa: str | None = None
