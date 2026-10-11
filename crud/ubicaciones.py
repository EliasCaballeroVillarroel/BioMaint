
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Ubicacion


def listar_ubicaciones(session: Session) -> list[Ubicacion]:
    stmt = select(Ubicacion).order_by(Ubicacion.id)
    return list(session.scalars(stmt).all())


def obtener_ubicacion(
    session: Session,
    ubicacion_id: int
) -> Ubicacion | None:
    return session.get(Ubicacion, ubicacion_id)


def crear_ubicacion(
    session: Session,
    clinica_id: int,
    servicio: str | None = None,
    sector: str | None = None,
    piso: str | None = None,
    sala: str | None = None
) -> Ubicacion:
    ubicacion = Ubicacion(
        clinica_id=clinica_id,
        servicio=servicio,
        sector=sector,
        piso=piso,
        sala=sala
    )

    session.add(ubicacion)
    session.commit()
    session.refresh(ubicacion)

    return ubicacion


def actualizar_ubicacion(
    session: Session,
    ubicacion_id: int,
    clinica_id: int | None = None,
    servicio: str | None = None,
    sector: str | None = None,
    piso: str | None = None,
    sala: str | None = None
) -> Ubicacion | None:
    ubicacion = session.get(Ubicacion, ubicacion_id)

    if ubicacion is None:
        return None

    if clinica_id is not None:
        ubicacion.clinica_id = clinica_id

    if servicio is not None:
        ubicacion.servicio = servicio

    if sector is not None:
        ubicacion.sector = sector

    if piso is not None:
        ubicacion.piso = piso

    if sala is not None:
        ubicacion.sala = sala

    session.commit()
    session.refresh(ubicacion)

    return ubicacion



def eliminar_ubicacion(
    session: Session,
    ubicacion_id: int
) -> bool:
    ubicacion = session.get(Ubicacion, ubicacion_id)

    if ubicacion is None:
        return False

    if ubicacion.equipos:
        return False

    session.delete(ubicacion)
    session.commit()

    return True



def listar_equipos_ubicacion(
    session: Session,
    ubicacion_id: int
):
    ubicacion = session.get(Ubicacion, ubicacion_id)

    if ubicacion is None:
        return None

    return ubicacion.equipos
