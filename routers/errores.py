from fastapi import HTTPException

from crud.errores import NoEncontradoError

# Formato común de los mensajes: oración completa, en voseo
# y con punto final.


def no_existe(recurso: str, recurso_id: int) -> HTTPException:
    # recurso va con su artículo indefinido, por ejemplo "un equipo".
    return HTTPException(
        status_code=404,
        detail=str(NoEncontradoError(recurso, recurso_id)),
    )


def sin_campos_para_actualizar() -> HTTPException:
    return HTTPException(
        status_code=400,
        detail="Debés enviar al menos un campo para actualizar.",
    )
