
from pydantic import BaseModel, ConfigDict, Field


class ClinicaCreate(BaseModel):
    nombre: str = Field(min_length=1, max_length=100)
    direccion: str | None = Field(default=None, max_length=200)


class ClinicaUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1, max_length=100)
    direccion: str | None = Field(default=None, max_length=200)


class ClinicaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    direccion: str | None = None
