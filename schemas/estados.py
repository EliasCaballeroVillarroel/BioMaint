from enum import Enum   

class EstadoEquipo(str, Enum):
    ACTIVO = "activo"
    INACTIVO = "inactivo"
    MANTENIMIENTO = "mantenimiento"