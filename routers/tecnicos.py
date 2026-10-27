from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from crud.tecnicos import (
    actualizar_tecnico,
    crear_tecnico,
    eliminar_tecnico,
    listar_mantenimientos_tecnico,
    listar_tecnicos,
    obtener_tecnico,
)
from database.dependencies import obtener_sesion
from routers.errores import no_existe, sin_campos_para_actualizar
from schemas.mantenimientos import MantenimientoResponse
from schemas.tecnicos import (
    TecnicoCreate,
    TecnicoResponse,
    TecnicoUpdate,
)

router = APIRouter(tags=["Técnicos"])


@router.get("/tecnicos", response_model=list[TecnicoResponse])
def listar(session: Session = Depends(obtener_sesion)):
    return listar_tecnicos(session)


@router.get("/tecnicos/{tecnico_id}", response_model=TecnicoResponse)
def obtener(tecnico_id: int, session: Session = Depends(obtener_sesion)):
    tecnico = obtener_tecnico(session, tecnico_id)

    if tecnico is None:
        raise no_existe("un técnico", tecnico_id)

    return tecnico


@router.post(
    "/tecnicos", response_model=TecnicoResponse, status_code=status.HTTP_201_CREATED
)
def crear(datos: TecnicoCreate, session: Session = Depends(obtener_sesion)):
    return crear_tecnico(
        session=session,
        nombre=datos.nombre,
        apellido=datos.apellido,
        empresa=datos.empresa,
    )


@router.put("/tecnicos/{tecnico_id}", response_model=TecnicoResponse)
def actualizar(
    tecnico_id: int, datos: TecnicoUpdate, session: Session = Depends(obtener_sesion)
):
    tecnico = obtener_tecnico(session, tecnico_id)

    if tecnico is None:
        raise no_existe("un técnico", tecnico_id)

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise sin_campos_para_actualizar()

    return actualizar_tecnico(
        session=session,
        tecnico_id=tecnico_id,
        **cambios,
    )


@router.delete("/tecnicos/{tecnico_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar(tecnico_id: int, session: Session = Depends(obtener_sesion)):
    eliminado = eliminar_tecnico(session, tecnico_id)

    if not eliminado:
        raise no_existe("un técnico", tecnico_id)



@router.get(
    "/tecnicos/{tecnico_id}/mantenimientos", response_model=list[MantenimientoResponse]
)
def listar_mantenimientos(tecnico_id: int, session: Session = Depends(obtener_sesion)):
    mantenimientos = listar_mantenimientos_tecnico(session, tecnico_id)

    if mantenimientos is None:
        raise no_existe("un técnico", tecnico_id)

    return mantenimientos
