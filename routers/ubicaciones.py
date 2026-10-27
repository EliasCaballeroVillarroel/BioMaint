from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from crud.ubicaciones import (
    actualizar_ubicacion,
    crear_ubicacion,
    eliminar_ubicacion,
    listar_equipos_ubicacion,
    listar_ubicaciones,
    obtener_ubicacion,
)
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar
from schemas.equipos import EquipoResponse
from schemas.ubicaciones import (
    UbicacionCreate,
    UbicacionResponse,
    UbicacionUpdate,
)

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

    ubicacion = actualizar_ubicacion(
        session,
        ubicacion_id,
        **cambios,
    )

    if ubicacion is None:
        raise no_existe("una ubicación", ubicacion_id)

    return ubicacion


@router.delete("/ubicaciones/{ubicacion_id}")
def eliminar(
    ubicacion_id: int,
    session: Session = Depends(obtener_sesion),
):
    eliminada = eliminar_ubicacion(session, ubicacion_id)

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
