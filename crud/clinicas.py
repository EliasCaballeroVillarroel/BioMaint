
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Clinica


def listar_clinicas(session: Session) -> list[Clinica]:
    stmt = select(Clinica).order_by(Clinica.id)
    return list(session.scalars(stmt).all())


def obtener_clinica(
    session: Session,
    clinica_id: int
) -> Clinica | None:
    return session.get(Clinica, clinica_id)


def crear_clinica(
    session: Session,
    nombre: str,
    direccion: str | None = None
) -> Clinica:
    clinica = Clinica(
        nombre=nombre,
        direccion=direccion
    )

    session.add(clinica)
    session.commit()
    session.refresh(clinica)

    return clinica


def actualizar_clinica(
    session: Session,
    clinica_id: int,
    nombre: str | None = None,
    direccion: str | None = None
) -> Clinica | None:
    clinica = session.get(Clinica, clinica_id)

    if clinica is None:
        return None

    if nombre is not None:
        clinica.nombre = nombre

    if direccion is not None:
        clinica.direccion = direccion

    session.commit()
    session.refresh(clinica)

    return clinica


def eliminar_clinica(
    session: Session,
    clinica_id: int
) -> bool:
    clinica = session.get(Clinica, clinica_id)

    if clinica is None:
        return False

    session.delete(clinica)
    session.commit()

    return True


def listar_ubicaciones_clinica(
    session: Session,
    clinica_id: int
):
    clinica = session.get(Clinica, clinica_id)

    if clinica is None:
        return None

    return clinica.ubicaciones
