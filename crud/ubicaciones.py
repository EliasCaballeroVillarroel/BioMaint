
from sqlalchemy import select
from sqlalchemy.orm import Session

from crud.transacciones import confirmar
from models import Ubicacion


def listar_ubicaciones(
    session: Session,
    incluir_inactivas: bool = False
) -> list[Ubicacion]:
    stmt = select(Ubicacion).order_by(Ubicacion.id)

    if not incluir_inactivas:
        stmt = stmt.where(Ubicacion.activa.is_(True))

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

    confirmar(session)

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

    # Se reactiva solo junto con su clínica (POST /clinicas/{id}/reactivar).
    if not ubicacion.activa:
        raise ValueError(
            "No se puede modificar una ubicación dada de baja."
        )

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

    confirmar(session)

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
        raise ValueError(
            "No se puede eliminar la ubicación porque tiene equipos asociados."
        )

    session.delete(ubicacion)

    confirmar(session)

    return True


def listar_equipos_ubicacion(
    session: Session,
    ubicacion_id: int
):
    ubicacion = session.get(Ubicacion, ubicacion_id)

    if ubicacion is None:
        return None

    return ubicacion.equipos
