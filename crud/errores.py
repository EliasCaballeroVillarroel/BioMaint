"""
Excepciones de las reglas de negocio.

El CRUD las lanza y main.py las traduce a respuestas HTTP, así las
reglas se cumplen aunque el CRUD se use por fuera de la API.
"""


class ReglaNegocioError(Exception):
    """Base de los errores de negocio; el mensaje va al cliente."""


class NoEncontradoError(ReglaNegocioError):
    """Un registro referenciado no existe (404)."""

    def __init__(self, recurso: str, recurso_id: int):
        # recurso va con su artículo indefinido, por ejemplo "un equipo".
        super().__init__(f"No existe {recurso} con ID {recurso_id}.")


class ConflictoError(ReglaNegocioError):
    """La operación choca con el estado actual de los datos (409)."""


class DatosInvalidosError(ReglaNegocioError):
    """Los datos son válidos por separado pero no en conjunto (422)."""
