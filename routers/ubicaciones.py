from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

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
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar

router = APIRouter(tags=["Ubicaciones"])


@router.get(
    "/ubicaciones",
    response_model=list[UbicacionResponse],
)
def listar(
    incluir_inactivas: bool = False,
    session: Session = Depends(obtener_sesion),
):
    return listar_ubicaciones(session, incluir_inactivas=incluir_inactivas)


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
        raise no_existe("una ubicación", ubicacion_id)

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
        raise no_existe("una clínica", datos.clinica_id)

    if not clinica.activa:
        raise HTTPException(
            status_code=409,
            detail="No se pueden crear ubicaciones en una clínica dada de baja.",
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
        raise sin_campos_para_actualizar()

    if "clinica_id" in cambios and cambios["clinica_id"] is not None:
        clinica = session.get(Clinica, cambios["clinica_id"])

        if clinica is None:
            raise no_existe("una clínica", cambios["clinica_id"])

        if not clinica.activa:
            raise HTTPException(
                status_code=409,
                detail="No se puede mover una ubicación a una clínica dada de baja.",
            )

    try:
        ubicacion = actualizar_ubicacion(
            session,
            ubicacion_id,
            **cambios,
        )
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if ubicacion is None:
        raise no_existe("una ubicación", ubicacion_id)

    return ubicacion


@router.delete("/ubicaciones/{ubicacion_id}")
def eliminar(
    ubicacion_id: int,
    session: Session = Depends(obtener_sesion),
):
    try:
        eliminada = eliminar_ubicacion(session, ubicacion_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if not eliminada:
        raise no_existe("una ubicación", ubicacion_id)

    return {
        "mensaje": f"La ubicación con ID {ubicacion_id} fue eliminada correctamente."
    }


@router.get(
    "/ubicaciones/{ubicacion_id}/equipos",
    response_model=list[EquipoResponse],
)
def listar_equipos_de_ubicacion(
    ubicacion_id: int,
    session: Session = Depends(obtener_sesion),
):
    equipos = listar_equipos_ubicacion(session, ubicacion_id)

    if equipos is None:
        raise no_existe("una ubicación", ubicacion_id)

    return equipos
