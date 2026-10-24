from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from crud.equipos import (
    listar_equipos,
    obtener_equipo,
    crear_equipo,
    actualizar_equipo,
    eliminar_equipo,
    dar_de_baja_equipo,
    NumeroSerieDuplicadoError,
)
from models import Ubicacion
from schemas.equipos import (
    EquipoCreate,
    EquipoUpdate,
    EquipoResponse,
)
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar


router = APIRouter(tags=["Equipos"])


@router.get("/equipos", response_model=list[EquipoResponse])
def listar_equipos_api(
    session: Session = Depends(obtener_sesion)
):
    return listar_equipos(session)


@router.get("/equipos/{equipo_id}", response_model=EquipoResponse)
def obtener_equipo_api(
    equipo_id: int,
    session: Session = Depends(obtener_sesion)
):
    equipo = obtener_equipo(session, equipo_id)

    if equipo is None:
        raise no_existe("un equipo", equipo_id)

    return equipo


@router.post(
    "/equipos",
    response_model=EquipoResponse,
    status_code=201
)
def crear_equipo_api(
    datos: EquipoCreate,
    session: Session = Depends(obtener_sesion)
):
    ubicacion = session.get(Ubicacion, datos.ubicacion_id)

    if ubicacion is None:
        raise no_existe("una ubicación", datos.ubicacion_id)

    if not ubicacion.activa:
        raise HTTPException(
            status_code=409,
            detail="No se pueden crear equipos en una ubicación dada de baja."
        )

    try:
        equipo = crear_equipo(
            session,
            nombre=datos.nombre,
            ubicacion_id=datos.ubicacion_id,
            estado_actual=datos.estado_actual.value,
            tipo=datos.tipo,
            modelo=datos.modelo,
            marca=datos.marca,
            numero_serie=datos.numero_serie
        )
    except NumeroSerieDuplicadoError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    return equipo


@router.put(
    "/equipos/{equipo_id}",
    response_model=EquipoResponse
)
def actualizar_equipo_api(
    equipo_id: int,
    datos: EquipoUpdate,
    session: Session = Depends(obtener_sesion)
):
    equipo = obtener_equipo(session, equipo_id)

    if equipo is None:
        raise no_existe("un equipo", equipo_id)

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise sin_campos_para_actualizar()

    # El schema ya rechaza null en estado_actual y ubicacion_id.
    if "estado_actual" in cambios:
        cambios["estado_actual"] = cambios["estado_actual"].value

    nueva_ubicacion_id = cambios.get("ubicacion_id")

    # Solo se valida un traslado real: un equipo en una ubicación
    # dada de baja puede seguir actualizándose sin moverse.
    if (
        nueva_ubicacion_id is not None
        and nueva_ubicacion_id != equipo.ubicacion_id
    ):
        ubicacion = session.get(Ubicacion, nueva_ubicacion_id)

        if ubicacion is None:
            raise no_existe("una ubicación", nueva_ubicacion_id)

        if not ubicacion.activa:
            raise HTTPException(
                status_code=409,
                detail="No se puede mover un equipo a una ubicación dada de baja."
            )

    try:
        return actualizar_equipo(session, equipo_id, **cambios)
    except (NumeroSerieDuplicadoError, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc


@router.delete("/equipos/{equipo_id}")
def eliminar_equipo_api(
    equipo_id: int,
    session: Session = Depends(obtener_sesion)
):
    try:
        eliminado = eliminar_equipo(session, equipo_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    if not eliminado:
        raise no_existe("un equipo", equipo_id)

    return {
        "mensaje": f"El equipo con ID {equipo_id} fue eliminado correctamente."
    }


@router.post(
    "/equipos/{equipo_id}/baja",
    response_model=EquipoResponse,
)
def dar_de_baja_equipo_api(
    equipo_id: int,
    session: Session = Depends(obtener_sesion),
):
    equipo = dar_de_baja_equipo(session, equipo_id)

    if equipo is None:
        raise no_existe("un equipo", equipo_id)

    return equipo
