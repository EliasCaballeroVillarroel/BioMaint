from collections.abc import Generator
from fastapi import APIRouter, Depends, HTTPException, FastAPI, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from database.db import SessionLocal
from crud.equipos import (
    listar_equipos,
    obtener_equipo,
    crear_equipo,
    actualizar_equipo,
    eliminar_equipo,
    NumeroSerieDuplicadoError,
)
from models import Equipo, Ubicacion
from schemas.equipos import (
    EquipoCreate,
    EquipoUpdate,
    EquipoResponse,
)

router = APIRouter(tags=["Equipos"])


def obtener_sesion():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()



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
        raise HTTPException(
            status_code=404,
            detail=f"No existe un equipo con ID {equipo_id}"
        )

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
    # Verificamos que la ubicación exista
    ubicacion = session.get(Ubicacion, datos.ubicacion_id)

    if ubicacion is None:
        raise HTTPException(
            status_code=404,
            detail=f"No existe una ubicación con ID {datos.ubicacion_id}"
        )

    # Creamos el equipo usando el CRUD existente
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
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        ) from exc

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
    cambios = datos.model_dump(exclude_unset=True)

    if "estado_actual" in cambios and cambios["estado_actual"] is not None:
        cambios["estado_actual"] = cambios["estado_actual"].value

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="Debes enviar al menos un campo para actualizar"
        )

    # Si se cambia la ubicación, verificamos que exista
    if "ubicacion_id" in cambios:
        ubicacion = session.get(Ubicacion, cambios["ubicacion_id"])

        if ubicacion is None:
            raise HTTPException(
                status_code=404,
                detail=f"No existe una ubicación con ID {cambios['ubicacion_id']}"
            )

        # El CRUD actual no recibe ubicacion_id.
        # Por eso la aplicamos directamente al objeto después.
        nueva_ubicacion_id = cambios.pop("ubicacion_id")
    else:
        nueva_ubicacion_id = None

    try:
        equipo = actualizar_equipo(
            session,
            equipo_id,
            **cambios
        )
    except NumeroSerieDuplicadoError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc)
        ) from exc

    if equipo is None:
        raise HTTPException(
            status_code=404,
            detail=f"No existe un equipo con ID {equipo_id}"
        )

    if nueva_ubicacion_id is not None:
        equipo.ubicacion_id = nueva_ubicacion_id
        session.commit()
        session.refresh(equipo)

    return equipo

@router.delete("/equipos/{equipo_id}")
def eliminar_equipo_api(
    equipo_id: int,
    session: Session = Depends(obtener_sesion)
):
    equipo = obtener_equipo(session, equipo_id)

    if equipo is None:
        raise HTTPException(
            status_code=404,
            detail=f"No existe un equipo con ID {equipo_id}"
        )

    eliminado = eliminar_equipo(session, equipo_id)

    if not eliminado:
        raise HTTPException(
            status_code=404,
            detail=f"No existe un equipo con ID {equipo_id}"
        )

    return {
        "mensaje": f"El equipo con ID {equipo_id} fue eliminado correctamente"
    }
