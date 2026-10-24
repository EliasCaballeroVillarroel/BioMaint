from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from crud.clinicas import (
    listar_clinicas,
    obtener_clinica,
    crear_clinica,
    actualizar_clinica,
    eliminar_clinica,
    dar_de_baja_clinica,
    reactivar_clinica,
)
from schemas.clinicas import (
    ClinicaCreate,
    ClinicaUpdate,
    ClinicaResponse,
)
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar


router = APIRouter(tags=["Clínicas"])



@router.get("/clinicas", response_model=list[ClinicaResponse])
def listar(
    incluir_inactivas: bool = False,
    session: Session = Depends(obtener_sesion),
):
    return listar_clinicas(session, incluir_inactivas=incluir_inactivas)


@router.get("/clinicas/{clinica_id}", response_model=ClinicaResponse)
def obtener(
    clinica_id: int,
    session: Session = Depends(obtener_sesion),
):
    clinica = obtener_clinica(session, clinica_id)

    if clinica is None:
        raise no_existe("una clínica", clinica_id)

    return clinica


@router.post(
    "/clinicas",
    response_model=ClinicaResponse,
    status_code=201,
)
def crear(
    datos: ClinicaCreate,
    session: Session = Depends(obtener_sesion),
):
    return crear_clinica(
        session,
        nombre=datos.nombre,
        direccion=datos.direccion,
    )


@router.put("/clinicas/{clinica_id}", response_model=ClinicaResponse)
def actualizar(
    clinica_id: int,
    datos: ClinicaUpdate,
    session: Session = Depends(obtener_sesion),
):
    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise sin_campos_para_actualizar()

    clinica = actualizar_clinica(
        session,
        clinica_id,
        **cambios,
    )

    if clinica is None:
        raise no_existe("una clínica", clinica_id)

    return clinica


@router.delete("/clinicas/{clinica_id}")
def eliminar(
    clinica_id: int,
    session: Session = Depends(obtener_sesion),
):
    eliminada = eliminar_clinica(session, clinica_id)

    if not eliminada:
        raise no_existe("una clínica", clinica_id)

    return {
        "mensaje": f"La clínica con ID {clinica_id} fue eliminada correctamente."
    }


@router.post(
    "/clinicas/{clinica_id}/baja",
    response_model=ClinicaResponse,
)
def dar_de_baja(
    clinica_id: int,
    session: Session = Depends(obtener_sesion),
):
    clinica = dar_de_baja_clinica(session, clinica_id)

    if clinica is None:
        raise no_existe("una clínica", clinica_id)

    return clinica


@router.post(
    "/clinicas/{clinica_id}/reactivar",
    response_model=ClinicaResponse,
)
def reactivar(
    clinica_id: int,
    session: Session = Depends(obtener_sesion),
):
    clinica = reactivar_clinica(session, clinica_id)

    if clinica is None:
        raise no_existe("una clínica", clinica_id)

    return clinica
