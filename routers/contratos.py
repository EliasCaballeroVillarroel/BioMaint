from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from crud.contratos import (
    actualizar_contrato,
    cancelar_contrato,
    crear_contrato,
    eliminar_contrato,
    listar_contratos,
    listar_contratos_equipo,
    obtener_contrato,
)
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar
from schemas.contratos import (
    ContratoCreate,
    ContratoResponse,
    ContratoUpdate,
)

router = APIRouter(tags=["Contratos"])


@router.get("/contratos", response_model=list[ContratoResponse])
def listar(session: Session = Depends(obtener_sesion)):
    return listar_contratos(session)


@router.get("/contratos/{contrato_id}", response_model=ContratoResponse)
def obtener(contrato_id: int, session: Session = Depends(obtener_sesion)):
    contrato = obtener_contrato(session, contrato_id)

    if contrato is None:
        raise no_existe("un contrato", contrato_id)

    return contrato


@router.post(
    "/contratos", response_model=ContratoResponse, status_code=status.HTTP_201_CREATED
)
def crear(datos: ContratoCreate, session: Session = Depends(obtener_sesion)):
    return crear_contrato(
        session=session,
        equipo_id=datos.equipo_id,
        tipo_contrato=datos.tipo_contrato,
        empresa=datos.empresa,
        fecha_inicio=datos.fecha_inicio,
        fecha_fin=datos.fecha_fin,
    )


@router.put("/contratos/{contrato_id}", response_model=ContratoResponse)
def actualizar(
    contrato_id: int, datos: ContratoUpdate, session: Session = Depends(obtener_sesion)
):
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise sin_campos_para_actualizar()

    contrato = actualizar_contrato(
        session=session,
        contrato_id=contrato_id,
        **cambios,
        # Así un null enviado (por ejemplo fecha_fin) se aplica.
        campos_enviados=set(cambios.keys()),
    )

    if contrato is None:
        raise no_existe("un contrato", contrato_id)

    return contrato


@router.delete("/contratos/{contrato_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(contrato_id: int, session: Session = Depends(obtener_sesion)):
    if not eliminar_contrato(session, contrato_id):
        raise no_existe("un contrato", contrato_id)



@router.post("/contratos/{contrato_id}/cancelar", response_model=ContratoResponse)
def cancelar(contrato_id: int, session: Session = Depends(obtener_sesion)):
    contrato = cancelar_contrato(session, contrato_id)

    if contrato is None:
        raise no_existe("un contrato", contrato_id)

    return contrato


@router.get("/equipos/{equipo_id}/contratos", response_model=list[ContratoResponse])
def listar_por_equipo(equipo_id: int, session: Session = Depends(obtener_sesion)):
    contratos = listar_contratos_equipo(session, equipo_id)

    if contratos is None:
        raise no_existe("un equipo", equipo_id)

    return contratos
