
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import SessionLocal
from schemas.tecnicos import (
    TecnicoCreate,
    TecnicoUpdate,
    TecnicoResponse,
)
from schemas.mantenimientos import MantenimientoResponse
from crud.tecnicos import (
    listar_tecnicos,
    obtener_tecnico,
    crear_tecnico,
    actualizar_tecnico,
    eliminar_tecnico,
    listar_mantenimientos_tecnico,
)


router = APIRouter(tags=["Técnicos"])


def obtener_sesion() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get(
    "/tecnicos",
    response_model=list[TecnicoResponse]
)
def listar(
    session: Session = Depends(obtener_sesion)
):
    return listar_tecnicos(session)


@router.get(
    "/tecnicos/{tecnico_id}",
    response_model=TecnicoResponse
)
def obtener(
    tecnico_id: int,
    session: Session = Depends(obtener_sesion)
):
    tecnico = obtener_tecnico(session, tecnico_id)

    if tecnico is None:
        raise HTTPException(
            status_code=404,
            detail="El técnico indicado no existe."
        )

    return tecnico


@router.post(
    "/tecnicos",
    response_model=TecnicoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear(
    datos: TecnicoCreate,
    session: Session = Depends(obtener_sesion)
):
    return crear_tecnico(
        session=session,
        nombre=datos.nombre,
        apellido=datos.apellido,
        empresa=datos.empresa,
    )


@router.put(
    "/tecnicos/{tecnico_id}",
    response_model=TecnicoResponse
)
def actualizar(
    tecnico_id: int,
    datos: TecnicoUpdate,
    session: Session = Depends(obtener_sesion)
):
    tecnico = obtener_tecnico(session, tecnico_id)

    if tecnico is None:
        raise HTTPException(
            status_code=404,
            detail="El técnico indicado no existe."
        )

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="Debés enviar al menos un campo para actualizar."
        )

    # Nombre y apellido no pueden quedar en null.
    for campo in ("nombre", "apellido"):
        if campo in cambios and cambios[campo] is None:
            raise HTTPException(
                status_code=422,
                detail=f"El campo '{campo}' no puede ser null."
            )

    return actualizar_tecnico(
        session=session,
        tecnico_id=tecnico_id,
        **cambios,
    )


@router.delete(
    "/tecnicos/{tecnico_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar(
    tecnico_id: int,
    session: Session = Depends(obtener_sesion)
):
    tecnico = obtener_tecnico(session, tecnico_id)

    if tecnico is None:
        raise HTTPException(
            status_code=404,
            detail="El técnico indicado no existe."
        )

    if tecnico.mantenimientos:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar el técnico porque "
                "tiene mantenimientos asociados."
            )
        )

    eliminar_tecnico(session, tecnico_id)

    return None


@router.get(
    "/tecnicos/{tecnico_id}/mantenimientos",
    response_model=list[MantenimientoResponse]
)
def listar_mantenimientos(
    tecnico_id: int,
    session: Session = Depends(obtener_sesion)
):
    mantenimientos = listar_mantenimientos_tecnico(
        session,
        tecnico_id
    )

    if mantenimientos is None:
        raise HTTPException(
            status_code=404,
            detail="El técnico indicado no existe."
        )

    return mantenimientos
