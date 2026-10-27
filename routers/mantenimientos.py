from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from crud.mantenimientos import (
    actualizar_mantenimiento,
    asignar_tecnico,
    crear_mantenimiento,
    desasignar_tecnico,
    eliminar_mantenimiento,
    listar_mantenimientos,
    listar_mantenimientos_equipo,
    obtener_mantenimiento,
)
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar
from schemas.mantenimientos import (
    MantenimientoCreate,
    MantenimientoResponse,
    MantenimientoUpdate,
)

router = APIRouter(tags=["Mantenimientos"])


@router.get("/mantenimientos", response_model=list[MantenimientoResponse])
def listar(session: Session = Depends(obtener_sesion)):
    return listar_mantenimientos(session)


@router.get("/mantenimientos/{mantenimiento_id}", response_model=MantenimientoResponse)
def obtener(mantenimiento_id: int, session: Session = Depends(obtener_sesion)):
    mantenimiento = obtener_mantenimiento(session, mantenimiento_id)

    if mantenimiento is None:
        raise no_existe("un mantenimiento", mantenimiento_id)

    return mantenimiento


@router.post(
    "/mantenimientos",
    response_model=MantenimientoResponse,
    status_code=status.HTTP_201_CREATED,
)
def crear(datos: MantenimientoCreate, session: Session = Depends(obtener_sesion)):
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


@router.put("/mantenimientos/{mantenimiento_id}", response_model=MantenimientoResponse)
def actualizar(
    mantenimiento_id: int,
    datos: MantenimientoUpdate,
    session: Session = Depends(obtener_sesion),
):
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise sin_campos_para_actualizar()

    mantenimiento = actualizar_mantenimiento(
        session=session,
        mantenimiento_id=mantenimiento_id,
        **cambios,
        # Así un null enviado (por ejemplo falla_id) se aplica.
        campos_enviados=set(cambios.keys()),
    )

    if mantenimiento is None:
        raise no_existe("un mantenimiento", mantenimiento_id)

    return mantenimiento


@router.delete(
    "/mantenimientos/{mantenimiento_id}", status_code=status.HTTP_204_NO_CONTENT
)
def eliminar(mantenimiento_id: int, session: Session = Depends(obtener_sesion)):
    if not eliminar_mantenimiento(session, mantenimiento_id):
        raise no_existe("un mantenimiento", mantenimiento_id)


@router.get(
    "/equipos/{equipo_id}/mantenimientos", response_model=list[MantenimientoResponse]
)
def listar_por_equipo(equipo_id: int, session: Session = Depends(obtener_sesion)):
    mantenimientos = listar_mantenimientos_equipo(session, equipo_id)

    if mantenimientos is None:
        raise no_existe("un equipo", equipo_id)

    return mantenimientos


@router.post(
    "/mantenimientos/{mantenimiento_id}/tecnicos/{tecnico_id}",
    response_model=MantenimientoResponse,
)
def asignar(
    mantenimiento_id: int, tecnico_id: int, session: Session = Depends(obtener_sesion)
):
    return asignar_tecnico(session, mantenimiento_id, tecnico_id)


@router.delete(
    "/mantenimientos/{mantenimiento_id}/tecnicos/{tecnico_id}",
    response_model=MantenimientoResponse,
)
def desasignar(
    mantenimiento_id: int, tecnico_id: int, session: Session = Depends(obtener_sesion)
):
    return desasignar_tecnico(session, mantenimiento_id, tecnico_id)
