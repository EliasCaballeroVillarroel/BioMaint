
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.db import SessionLocal
from models import Equipo, Falla
from schemas.mantenimientos import (
    MantenimientoCreate,
    MantenimientoUpdate,
    MantenimientoResponse,
)
from crud.mantenimientos import (
    listar_mantenimientos,
    obtener_mantenimiento,
    crear_mantenimiento,
    actualizar_mantenimiento,
    eliminar_mantenimiento,
    listar_mantenimientos_equipo,
    asignar_tecnico,
)


router = APIRouter(tags=["Mantenimientos"])


def obtener_sesion() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get(
    "/mantenimientos",
    response_model=list[MantenimientoResponse]
)
def listar(
    session: Session = Depends(obtener_sesion)
):
    return listar_mantenimientos(session)


@router.get(
    "/mantenimientos/{mantenimiento_id}",
    response_model=MantenimientoResponse
)
def obtener(
    mantenimiento_id: int,
    session: Session = Depends(obtener_sesion)
):
    mantenimiento = obtener_mantenimiento(session, mantenimiento_id)

    if mantenimiento is None:
        raise HTTPException(
            status_code=404,
            detail="El mantenimiento indicado no existe."
        )

    return mantenimiento


@router.post(
    "/mantenimientos",
    response_model=MantenimientoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear(
    datos: MantenimientoCreate,
    session: Session = Depends(obtener_sesion)
):
    # Verificar que exista el equipo.
    equipo = session.get(Equipo, datos.equipo_id)

    if equipo is None:
        raise HTTPException(
            status_code=404,
            detail="El equipo indicado no existe."
        )

    # Si se indicó una falla, verificar que exista
    # y que corresponda al equipo seleccionado.
    if datos.falla_id is not None:
        falla = session.get(Falla, datos.falla_id)

        if falla is None:
            raise HTTPException(
                status_code=404,
                detail="La falla indicada no existe."
            )

        if falla.equipo_id != datos.equipo_id:
            raise HTTPException(
                status_code=422,
                detail="La falla no pertenece al equipo indicado."
            )

    return crear_mantenimiento(
        session=session,
        equipo_id=datos.equipo_id,
        falla_id=datos.falla_id,
        fecha=datos.fecha,
        tipo_mantenimiento=datos.tipo_mantenimiento,
        duracion_mantenimiento=datos.duracion_mantenimiento,
        descripcion=datos.descripcion,
        resultado=datos.resultado,
    )


@router.put(
    "/mantenimientos/{mantenimiento_id}",
    response_model=MantenimientoResponse
)
def actualizar(
    mantenimiento_id: int,
    datos: MantenimientoUpdate,
    session: Session = Depends(obtener_sesion)
):
    existente = obtener_mantenimiento(session, mantenimiento_id)

    if existente is None:
        raise HTTPException(
            status_code=404,
            detail="El mantenimiento indicado no existe."
        )

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="Debés enviar al menos un campo para actualizar."
        )

    # Estos campos son obligatorios en la base de datos.
    if cambios.get("fecha", existente.fecha) is None:
        raise HTTPException(
            status_code=422,
            detail="La fecha del mantenimiento no puede ser null."
        )

    if cambios.get(
        "tipo_mantenimiento", existente.tipo_mantenimiento
    ) is None:
        raise HTTPException(
            status_code=422,
            detail="El tipo de mantenimiento no puede ser null."
        )

    falla_id = cambios.get("falla_id", existente.falla_id)

    if falla_id is not None:
        falla = session.get(Falla, falla_id)

        if falla is None:
            raise HTTPException(
                status_code=404,
                detail="La falla indicada no existe."
            )

        if falla.equipo_id != existente.equipo_id:
            raise HTTPException(
                status_code=422,
                detail="La falla no pertenece al equipo del mantenimiento."
            )

    try:
        mantenimiento = actualizar_mantenimiento(
            session=session,
            mantenimiento_id=mantenimiento_id,
            **cambios,
            campos_enviados=set(cambios.keys()),
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error

    return mantenimiento


@router.delete(
    "/mantenimientos/{mantenimiento_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar(
    mantenimiento_id: int,
    session: Session = Depends(obtener_sesion)
):
    eliminado = eliminar_mantenimiento(session, mantenimiento_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail="El mantenimiento indicado no existe."
        )

    return None


@router.get(
    "/equipos/{equipo_id}/mantenimientos",
    response_model=list[MantenimientoResponse]
)
def listar_por_equipo(
    equipo_id: int,
    session: Session = Depends(obtener_sesion)
):
    mantenimientos = listar_mantenimientos_equipo(session, equipo_id)

    if mantenimientos is None:
        raise HTTPException(
            status_code=404,
            detail="El equipo indicado no existe."
        )

    return mantenimientos


@router.post(
    "/mantenimientos/{mantenimiento_id}/tecnicos/{tecnico_id}",
    response_model=MantenimientoResponse
)
def asignar(
    mantenimiento_id: int,
    tecnico_id: int,
    session: Session = Depends(obtener_sesion)
):
    try:
        return asignar_tecnico(
            session,
            mantenimiento_id,
            tecnico_id
        )
    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error)
        ) from error
