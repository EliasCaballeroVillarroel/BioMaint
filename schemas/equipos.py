from pydantic import BaseModel, Field, ConfigDict, field_validator
from schemas.estados import EstadoEquipo
from schemas.validadores import rechazar_null, rechazar_dado_de_baja


class EquipoCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    ubicacion_id: int = Field(gt=0)
    estado_actual: EstadoEquipo

    tipo: str | None = Field(default=None, max_length=100)
    modelo: str | None = Field(default=None, max_length=100)
    marca: str | None = Field(default=None, max_length=100)
    numero_serie: str | None = Field(default=None, min_length=1, max_length=100)

    # La baja tiene su propio endpoint.
    @field_validator("estado_actual")
    @classmethod
    def validar_estado(cls, estado):
        return rechazar_dado_de_baja(estado)


class EquipoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    ubicacion_id: int | None = Field(default=None, gt=0)
    estado_actual: EstadoEquipo | None = None

    tipo: str | None = Field(default=None, max_length=100)
    modelo: str | None = Field(default=None, max_length=100)
    marca: str | None = Field(default=None, max_length=100)
    numero_serie: str | None = Field(default=None, min_length=1, max_length=100)

    # Los campos obligatorios pueden omitirse, pero no enviarse como null.
    # (El validador solo corre si el campo viene en el body.)
    @field_validator("nombre", "ubicacion_id", "estado_actual")
    @classmethod
    def validar_no_nulo(cls, valor):
        return rechazar_null(valor)

    @field_validator("estado_actual")
    @classmethod
    def validar_estado(cls, estado):
        return rechazar_dado_de_baja(estado)


class EquipoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    ubicacion_id: int
    estado_actual: str
    tipo: str | None = None
    modelo: str | None = None
    marca: str | None = None
    numero_serie: str | None = None
    ubicacion_activa: bool
