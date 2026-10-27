# Importar este paquete carga todos los modelos y los registra en
# Base.metadata. Alembic, los tests y las relaciones de SQLAlchemy
# dependen de esto: no borrar estos imports aunque parezcan sin uso.

from models.clinicas import Clinica
from models.contratos import Contrato
from models.equipos import Equipo
from models.fallas import Falla
from models.mantenimiento_tecnicos import mantenimiento_tecnicos
from models.mantenimientos import Mantenimiento
from models.tecnicos import Tecnico
from models.ubicaciones import Ubicacion

__all__ = [
    "Clinica",
    "Contrato",
    "Equipo",
    "Falla",
    "Mantenimiento",
    "Tecnico",
    "Ubicacion",
    "mantenimiento_tecnicos",
]