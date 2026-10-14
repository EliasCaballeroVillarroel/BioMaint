
from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Equipo


class NumeroSerieDuplicadoError(Exception):
    pass


def verificar_numero_serie(
    session: Session,
    numero_serie: str | None,
    equipo_id_excluir: int | None = None
) -> None:
    if numero_serie is None:
        return

    stmt = select(Equipo).where(
        Equipo.numero_serie == numero_serie
    )

    if equipo_id_excluir is not None:
        stmt = stmt.where(Equipo.id != equipo_id_excluir)

    existe = session.scalar(stmt)

    if existe is not None:
        raise NumeroSerieDuplicadoError(
            f"Ya existe un equipo con número de serie '{numero_serie}'"
        )


def listar_equipos(session: Session) -> list[Equipo]:
    stmt = select(Equipo).order_by(Equipo.id)
    return list(session.scalars(stmt).all())


def obtener_equipo(
    session: Session,
    equipo_id: int
) -> Equipo | None:
    return session.get(Equipo, equipo_id)

def crear_equipo(
    session: Session,
    nombre: str,
    ubicacion_id: int,
    estado_actual: str,
    tipo: str | None = None,
    modelo: str | None = None,
    marca: str | None = None,
    numero_serie: str | None = None
) -> Equipo:

    equipo = Equipo(
        nombre=nombre,
        ubicacion_id=ubicacion_id,
        estado_actual=estado_actual,
        tipo=tipo,
        modelo=modelo,
        marca=marca,
        numero_serie=numero_serie
    )

    try:
        verificar_numero_serie(session, numero_serie)
        session.add(equipo)
        session.commit()
        session.refresh(equipo)

        return equipo

    except Exception:
        session.rollback()
        raise


def actualizar_equipo(
    session: Session,
    equipo_id: int,
    nombre: str | None = None,
    estado_actual: str | None = None,
    tipo: str | None = None,
    modelo: str | None = None,
    marca: str | None = None,
    numero_serie: str | None = None
) -> Equipo | None:

    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        return None

    try:
        if numero_serie is not None:
            verificar_numero_serie(
            session,
            numero_serie,
            equipo_id_excluir=equipo_id
        )
        if nombre is not None:
            equipo.nombre = nombre

        if estado_actual is not None:
            equipo.estado_actual = estado_actual

        if tipo is not None:
            equipo.tipo = tipo

        if modelo is not None:
            equipo.modelo = modelo

        if marca is not None:
            equipo.marca = marca

        if numero_serie is not None:
            equipo.numero_serie = numero_serie

        session.commit()
        session.refresh(equipo)

        return equipo

    except Exception:
        session.rollback()
        raise



def eliminar_equipo(
    session: Session,
    equipo_id: int
) -> bool:

    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        return False

    try:
        session.delete(equipo)
        session.commit()

        return True

    except Exception:
        session.rollback()
        raise
