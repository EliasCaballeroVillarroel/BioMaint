from pydantic import BaseModel, Field, ConfigDict
from schemas.estados import EstadoEquipo

class EquipoCreate(BaseModel):
    nombre: str = Field(min_length=1)
    ubicacion_id: int = Field(gt=0)
    estado_actual: EstadoEquipo

    tipo: str | None = None
    modelo: str | None = None
    marca: str | None = None
    numero_serie: str | None = Field(default=None, min_length=1)

class EquipoUpdate(BaseModel):
    nombre: str | None = Field(default=None, min_length=1)
    ubicacion_id: int | None = Field(default=None, gt=0)
    estado_actual: EstadoEquipo | None = None

    tipo: str | None = None
    modelo: str | None = None
    marca: str | None = None
    numero_serie: str | None = Field(default=None, min_length=1)

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


