
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Tecnico


def listar_tecnicos(session: Session) -> list[Tecnico]:
    stmt = select(Tecnico).order_by(Tecnico.id)
    return list(session.scalars(stmt).all())


def obtener_tecnico(
    session: Session,
    tecnico_id: int
) -> Tecnico | None:
    return session.get(Tecnico, tecnico_id)


def crear_tecnico(
    session: Session,
    nombre: str,
    apellido: str,
    empresa: str | None = None
) -> Tecnico:
    tecnico = Tecnico(
        nombre=nombre,
        apellido=apellido,
        empresa=empresa
    )

    session.add(tecnico)
    session.commit()
    session.refresh(tecnico)

    return tecnico


def actualizar_tecnico(
    session: Session,
    tecnico_id: int,
    nombre: str | None = None,
    apellido: str | None = None,
    empresa: str | None = None
) -> Tecnico | None:
    tecnico = session.get(Tecnico, tecnico_id)

    if tecnico is None:
        return None

    if nombre is not None:
        tecnico.nombre = nombre

    if apellido is not None:
        tecnico.apellido = apellido

    if empresa is not None:
        tecnico.empresa = empresa

    session.commit()
    session.refresh(tecnico)

    return tecnico


def eliminar_tecnico(
    session: Session,
    tecnico_id: int
) -> bool:
    tecnico = session.get(Tecnico, tecnico_id)

    if tecnico is None:
        return False

    if tecnico.mantenimientos:
        return False

    session.delete(tecnico)
    session.commit()

    return True


def listar_mantenimientos_tecnico(
    session: Session,
    tecnico_id: int
):
    tecnico = session.get(Tecnico, tecnico_id)

    if tecnico is None:
        return None

    return tecnico.mantenimientos
