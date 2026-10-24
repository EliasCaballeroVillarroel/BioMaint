
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar
from models import Equipo
from schemas.contratos import (
    ContratoCreate,
    ContratoUpdate,
    ContratoResponse,
)
from crud.contratos import (
    listar_contratos,
    obtener_contrato,
    crear_contrato,
    actualizar_contrato,
    eliminar_contrato,
    listar_contratos_equipo,

)


router = APIRouter(tags=["Contratos"])


@router.get(
    "/contratos",
    response_model=list[ContratoResponse]
)
def listar(
    session: Session = Depends(obtener_sesion)
):
    return listar_contratos(session)


@router.get(
    "/contratos/{contrato_id}",
    response_model=ContratoResponse
)
def obtener(
    contrato_id: int,
    session: Session = Depends(obtener_sesion)
):
    contrato = obtener_contrato(session, contrato_id)

    if contrato is None:
        raise no_existe("un contrato", contrato_id)

    return contrato


@router.post(
    "/contratos",
    response_model=ContratoResponse,
    status_code=status.HTTP_201_CREATED
)
def crear(
    datos: ContratoCreate,
    session: Session = Depends(obtener_sesion)
):
    equipo = session.get(Equipo, datos.equipo_id)

    if equipo is None:
        raise no_existe("un equipo", datos.equipo_id)

    return crear_contrato(
        session=session,
        equipo_id=datos.equipo_id,
        tipo_contrato=datos.tipo_contrato,
        empresa=datos.empresa,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
        estado=datos.estado,
    )


@router.put(
    "/contratos/{contrato_id}",
    response_model=ContratoResponse
)
def actualizar(
    contrato_id: int,
    datos: ContratoUpdate,
    session: Session = Depends(obtener_sesion)
):
    contrato = obtener_contrato(session, contrato_id)

    if contrato is None:
        raise no_existe("un contrato", contrato_id)

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise sin_campos_para_actualizar()

    # Comprobar las fechas resultantes, no solo las enviadas.
    fecha_inicio_final = cambios.get(
        "fecha_inicio", contrato.fecha_inicio
    )
    fecha_fin_final = cambios.get(
        "fecha_fin", contrato.fecha_fin
    )

    if fecha_inicio_final is None:
        raise HTTPException(
            status_code=422,
            detail="La fecha de inicio no puede ser nula."
        )

    if (
        fecha_fin_final is not None
        and fecha_fin_final < fecha_inicio_final
    ):
        raise HTTPException(
            status_code=422,
            detail="La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    try:
        return actualizar_contrato(
            session=session,
            contrato_id=contrato_id,
            **cambios,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error


@router.delete(
    "/contratos/{contrato_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
def eliminar(
    contrato_id: int,
    session: Session = Depends(obtener_sesion)
):
    eliminado = eliminar_contrato(session, contrato_id)

    if not eliminado:
        raise no_existe("un contrato", contrato_id)

    return None


@router.get(
    "/equipos/{equipo_id}/contratos",
    response_model=list[ContratoResponse]
)
def listar_por_equipo(
    equipo_id: int,
    session: Session = Depends(obtener_sesion)
):
    contratos = listar_contratos_equipo(session, equipo_id)

    if contratos is None:
        raise no_existe("un equipo", equipo_id)

    return contratos
