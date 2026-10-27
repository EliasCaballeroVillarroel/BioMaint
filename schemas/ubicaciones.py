from pydantic import BaseModel, ConfigDict, Field, field_validator

from schemas.validadores import rechazar_null


class UbicacionCreate(BaseModel):
    clinica_id: int = Field(gt=0)

    servicio: str | None = Field(default=None, max_length=100)
    sector: str | None = Field(default=None, max_length=100)
    piso: str | None = Field(default=None, max_length=20)
    sala: str | None = Field(default=None, max_length=50)


class UbicacionUpdate(BaseModel):
    clinica_id: int | None = Field(default=None, gt=0)

    servicio: str | None = Field(default=None, max_length=100)
    sector: str | None = Field(default=None, max_length=100)
    piso: str | None = Field(default=None, max_length=20)
    sala: str | None = Field(default=None, max_length=50)

    # La clínica puede omitirse, pero no enviarse como null.
    @field_validator("clinica_id")
    @classmethod
    def validar_no_nulo(cls, valor):
        return rechazar_null(valor)


class UbicacionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    clinica_id: int
    servicio: str | None = None
    sector: str | None = None
    piso: str | None = None
    sala: str | None = None
    activa: bool
