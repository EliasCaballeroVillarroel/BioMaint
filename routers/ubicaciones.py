
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import SessionLocal
from models import Clinica
from crud.ubicaciones import (
    listar_ubicaciones,
    obtener_ubicacion,
    crear_ubicacion,
    actualizar_ubicacion,
    eliminar_ubicacion,
    listar_equipos_ubicacion,
)
from schemas.ubicaciones import (
    UbicacionCreate,
    UbicacionUpdate,
    UbicacionResponse,
)
from schemas.equipos import EquipoResponse


router = APIRouter(tags=["Ubicaciones"])


def obtener_sesion() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get(
    "/ubicaciones",
    response_model=list[UbicacionResponse],
)
def listar(
    session: Session = Depends(obtener_sesion),
):
    return listar_ubicaciones(session)


@router.get(
    "/ubicaciones/{ubicacion_id}",
    response_model=UbicacionResponse,
)
def obtener(
    ubicacion_id: int,
    session: Session = Depends(obtener_sesion),
):
    ubicacion = obtener_ubicacion(session, ubicacion_id)

    if ubicacion is None:
        raise HTTPException(
            status_code=404,
            detail="Ubicación no encontrada",
        )

    return ubicacion


@router.post(
    "/ubicaciones",
    response_model=UbicacionResponse,
    status_code=201,
)
def crear(
    datos: UbicacionCreate,
    session: Session = Depends(obtener_sesion),
):
    clinica = session.get(Clinica, datos.clinica_id)

    if clinica is None:
        raise HTTPException(
            status_code=404,
            detail="La clínica indicada no existe",
        )

    return crear_ubicacion(
        session,
        clinica_id=datos.clinica_id,
        servicio=datos.servicio,
        sector=datos.sector,
        piso=datos.piso,
        sala=datos.sala,
    )


@router.put(
    "/ubicaciones/{ubicacion_id}",
    response_model=UbicacionResponse,
)
def actualizar(
    ubicacion_id: int,
    datos: UbicacionUpdate,
    session: Session = Depends(obtener_sesion),
):
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="Debés enviar al menos un campo para actualizar",
        )

    if "clinica_id" in cambios and cambios["clinica_id"] is not None:
        clinica = session.get(Clinica, cambios["clinica_id"])

        if clinica is None:
            raise HTTPException(
                status_code=404,
                detail="La clínica indicada no existe",
            )

    ubicacion = actualizar_ubicacion(
        session,
        ubicacion_id,
        **cambios,
    )

    if ubicacion is None:
        raise HTTPException(
            status_code=404,
            detail="Ubicación no encontrada",
        )

    return ubicacion


@router.delete("/ubicaciones/{ubicacion_id}")
def eliminar(
    ubicacion_id: int,
    session: Session = Depends(obtener_sesion),
):
    ubicacion = obtener_ubicacion(session, ubicacion_id)

    if ubicacion is None:
        raise HTTPException(
            status_code=404,
            detail="Ubicación no encontrada",
        )

    if ubicacion.equipos:
        raise HTTPException(
            status_code=409,
            detail=(
                "No se puede eliminar la ubicación porque "
                "tiene equipos asociados"
            ),
        )

    eliminar_ubicacion(session, ubicacion_id)

    return {"mensaje": "Ubicación eliminada correctamente"}


@router.get(
    "/ubicaciones/{ubicacion_id}/equipos",
    response_model=list[EquipoResponse],
)
def listar_equipos_de_ubicacion(
    ubicacion_id: int,
    session: Session = Depends(obtener_sesion),
):
    ubicacion = obtener_ubicacion(session, ubicacion_id)

    if ubicacion is None:
        raise HTTPException(
            status_code=404,
            detail="Ubicación no encontrada",
        )

    return listar_equipos_ubicacion(session, ubicacion_id)
