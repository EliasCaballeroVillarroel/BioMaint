from enum import Enum


class EstadoEquipo(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"
    DADO_DE_BAJA = "dado_de_baja"


class SeveridadFalla(str, Enum):
    BAJA = "baja"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"
