
from collections.abc import Generator

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import SessionLocal
from crud.clinicas import (
    listar_clinicas,
    obtener_clinica,
    crear_clinica,
    actualizar_clinica,
    eliminar_clinica,
)
from schemas.clinicas import (
    ClinicaCreate,
    ClinicaUpdate,
    ClinicaResponse,
)


router = APIRouter(tags=["Clínicas"])


def obtener_sesion() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.get("/clinicas", response_model=list[ClinicaResponse])
def listar(
    session: Session = Depends(obtener_sesion),
):
    return listar_clinicas(session)


@router.get("/clinicas/{clinica_id}", response_model=ClinicaResponse)
def obtener(
    clinica_id: int,
    session: Session = Depends(obtener_sesion),
):
    clinica = obtener_clinica(session, clinica_id)

    if clinica is None:
        raise HTTPException(
            status_code=404,
            detail="Clínica no encontrada",
        )

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
        raise HTTPException(
            status_code=400,
            detail="Debés enviar al menos un campo para actualizar",
        )

    clinica = actualizar_clinica(
        session,
        clinica_id,
        **cambios,
    )

    if clinica is None:
        raise HTTPException(
            status_code=404,
            detail="Clínica no encontrada",
        )

    return clinica


@router.delete("/clinicas/{clinica_id}")
def eliminar(
    clinica_id: int,
    session: Session = Depends(obtener_sesion),
):
    eliminada = eliminar_clinica(session, clinica_id)

    if not eliminada:
        raise HTTPException(
            status_code=404,
            detail="Clínica no encontrada",
        )

    return {"mensaje": "Clínica eliminada correctamente"}
