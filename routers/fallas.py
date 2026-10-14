
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import SessionLocal
from models import Equipo
from crud.fallas import (
    listar_fallas,
    obtener_falla,
    crear_falla,
    actualizar_falla,
    eliminar_falla,
    listar_fallas_equipo,
)
from schemas.fallas import (
    FallaCreate,
    FallaUpdate,
    FallaResponse,
)


router = APIRouter(tags=["Fallas"])


def obtener_sesion() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get("/fallas", response_model=list[FallaResponse])
def listar(
    session: Session = Depends(obtener_sesion),
):
    return listar_fallas(session)


@router.get("/fallas/{falla_id}", response_model=FallaResponse)
def obtener(
    falla_id: int,
    session: Session = Depends(obtener_sesion),
):
    falla = obtener_falla(session, falla_id)

    if falla is None:
        raise HTTPException(
            status_code=404,
            detail="Falla no encontrada",
        )

    return falla


@router.post(
    "/fallas",
    response_model=FallaResponse,
    status_code=201,
)
def crear(
    datos: FallaCreate,
    session: Session = Depends(obtener_sesion),
):
    equipo = session.get(Equipo, datos.equipo_id)

    if equipo is None:
        raise HTTPException(
            status_code=404,
            detail="El equipo indicado no existe",
        )

    return crear_falla(
        session,
        equipo_id=datos.equipo_id,
        tipo_falla=datos.tipo_falla,
        fecha_falla=datos.fecha_falla,
        descripcion_falla=datos.descripcion_falla,
        fecha_resolucion=datos.fecha_resolucion,
        severidad=datos.severidad,
    )


@router.put("/fallas/{falla_id}", response_model=FallaResponse)
def actualizar(
    falla_id: int,
    datos: FallaUpdate,
    session: Session = Depends(obtener_sesion),
):
    falla_existente = obtener_falla(session, falla_id)

    if falla_existente is None:
        raise HTTPException(
            status_code=404,
            detail="Falla no encontrada",
        )

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="Debés enviar al menos un campo para actualizar",
        )

    fecha_falla_final = (
        cambios.get("fecha_falla") or falla_existente.fecha_falla
    )
    fecha_resolucion_final = (
        cambios.get("fecha_resolucion")
        or falla_existente.fecha_resolucion
    )

    if (
        fecha_resolucion_final is not None
        and fecha_resolucion_final < fecha_falla_final
    ):
        raise HTTPException(
            status_code=422,
            detail=(
                "La fecha de resolución no puede ser anterior "
                "a la fecha de la falla"
            ),
        )

    cambios.pop("equipo_id", None)

    falla = actualizar_falla(
        session,
        falla_id,
        **cambios,
    )

    return falla


@router.delete("/fallas/{falla_id}")
def eliminar(
    falla_id: int,
    session: Session = Depends(obtener_sesion),
):
    falla = obtener_falla(session, falla_id)

    if falla is None:
        raise HTTPException(
            status_code=404,
            detail="Falla no encontrada",
        )

    if falla.mantenimientos:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar la falla porque "
                "tiene mantenimientos asociados"
            ),
        )

    eliminar_falla(session, falla_id)

    return {"mensaje": "Falla eliminada correctamente"}


@router.get(
    "/equipos/{equipo_id}/fallas",
    response_model=list[FallaResponse],
)
def listar_fallas_de_equipo(
    equipo_id: int,
    session: Session = Depends(obtener_sesion),
):
    fallas = listar_fallas_equipo(session, equipo_id)

    if fallas is None:
        raise HTTPException(
            status_code=404,
            detail="El equipo indicado no existe",
        )

    return fallas
