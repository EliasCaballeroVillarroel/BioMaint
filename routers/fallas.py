from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

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
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar


router = APIRouter(tags=["Fallas"])


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
        raise no_existe("una falla", falla_id)

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
    return crear_falla(
        session,
        equipo_id=datos.equipo_id,
        tipo_falla=datos.tipo_falla,
        fecha_falla=datos.fecha_falla,
        descripcion_falla=datos.descripcion_falla,
        fecha_resolucion=datos.fecha_resolucion,
        severidad=datos.severidad.value if datos.severidad else None,
    )


@router.put("/fallas/{falla_id}", response_model=FallaResponse)
def actualizar(
    falla_id: int,
    datos: FallaUpdate,
    session: Session = Depends(obtener_sesion),
):
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise sin_campos_para_actualizar()

    if cambios.get("severidad") is not None:
        cambios["severidad"] = cambios["severidad"].value

    falla = actualizar_falla(
        session,
        falla_id,
        **cambios,
    )

    if falla is None:
        raise no_existe("una falla", falla_id)

    return falla


@router.delete("/fallas/{falla_id}")
def eliminar(
    falla_id: int,
    session: Session = Depends(obtener_sesion),
):
    eliminada = eliminar_falla(session, falla_id)

    if not eliminada:
        raise no_existe("una falla", falla_id)

    return {
        "mensaje": f"La falla con ID {falla_id} fue eliminada correctamente."
    }


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
        raise no_existe("un equipo", equipo_id)

    return fallas
