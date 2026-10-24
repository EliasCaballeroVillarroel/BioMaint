
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


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
    equipo = session.get(Equipo, datos.equipo_id)

    if equipo is None:
        raise no_existe("un equipo", datos.equipo_id)

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
        raise no_existe("una falla", falla_id)

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise sin_campos_para_actualizar()

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
                "a la fecha de la falla."
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
    try:
        eliminada = eliminar_falla(session, falla_id)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

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
