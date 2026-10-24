
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from crud.transacciones import confirmar
from models import Mantenimiento, Equipo, Falla, Tecnico


def listar_mantenimientos(
    session: Session
) -> list[Mantenimiento]:
    stmt = select(Mantenimiento).order_by(Mantenimiento.id)
    return list(session.scalars(stmt).all())


def obtener_mantenimiento(
    session: Session,
    mantenimiento_id: int
) -> Mantenimiento | None:
    return session.get(Mantenimiento, mantenimiento_id)


def crear_mantenimiento(
    session: Session,
    equipo_id: int,
    fecha: date,
    tipo_mantenimiento: str,
    falla_id: int | None = None,
    duracion_mantenimiento: int | None = None,
    descripcion: str | None = None,
    resultado: str | None = None
) -> Mantenimiento:
    if session.get(Equipo, equipo_id) is None:
        raise ValueError(f"No existe un equipo con ID {equipo_id}.")

    if falla_id is not None:
        falla = session.get(Falla, falla_id)

        if falla is None:
            raise ValueError(f"No existe una falla con ID {falla_id}.")

        if falla.equipo_id != equipo_id:
            raise ValueError(
                "La falla no pertenece al equipo indicado."
            )

    mantenimiento = Mantenimiento(
        equipo_id=equipo_id,
        falla_id=falla_id,
        fecha=fecha,
        tipo_mantenimiento=tipo_mantenimiento,
        duracion_mantenimiento=duracion_mantenimiento,
        descripcion=descripcion,
        resultado=resultado
    )

    session.add(mantenimiento)

    confirmar(session)

    session.refresh(mantenimiento)
    return mantenimiento


def actualizar_mantenimiento(
    session: Session,
    mantenimiento_id: int,
    fecha: date | None = None,
    tipo_mantenimiento: str | None = None,
    falla_id: int | None = None,
    duracion_mantenimiento: int | None = None,
    descripcion: str | None = None,
    resultado: str | None = None,
    campos_enviados: set[str] | None = None
) -> Mantenimiento | None:
    mantenimiento = session.get(
        Mantenimiento,
        mantenimiento_id
    )

    if mantenimiento is None:
        return None

    # Compatibilidad con llamadas anteriores al CRUD.
    if campos_enviados is None:
        campos_enviados = {
            nombre
            for nombre, valor in {
                "fecha": fecha,
                "tipo_mantenimiento": tipo_mantenimiento,
                "falla_id": falla_id,
                "duracion_mantenimiento": duracion_mantenimiento,
                "descripcion": descripcion,
                "resultado": resultado,
            }.items()
            if valor is not None
        }

    if "falla_id" in campos_enviados and falla_id is not None:
        falla = session.get(Falla, falla_id)

        if falla is None:
            raise ValueError(f"No existe una falla con ID {falla_id}.")

        if falla.equipo_id != mantenimiento.equipo_id:
            raise ValueError(
                "La falla no pertenece al equipo del mantenimiento."
            )

    valores = {
        "fecha": fecha,
        "tipo_mantenimiento": tipo_mantenimiento,
        "falla_id": falla_id,
        "duracion_mantenimiento": duracion_mantenimiento,
        "descripcion": descripcion,
        "resultado": resultado,
    }

    for nombre in campos_enviados:
        if nombre in valores:
            setattr(mantenimiento, nombre, valores[nombre])

    confirmar(session)

    session.refresh(mantenimiento)
    return mantenimiento


def eliminar_mantenimiento(
    session: Session,
    mantenimiento_id: int
) -> bool:
    mantenimiento = session.get(
        Mantenimiento,
        mantenimiento_id
    )

    if mantenimiento is None:
        return False

    session.delete(mantenimiento)

    confirmar(session)

    return True


def listar_mantenimientos_equipo(
    session: Session,
    equipo_id: int
) -> list[Mantenimiento] | None:
    if session.get(Equipo, equipo_id) is None:
        return None

    stmt = (
        select(Mantenimiento)
        .where(Mantenimiento.equipo_id == equipo_id)
        .order_by(Mantenimiento.fecha.desc())
    )

    return list(session.scalars(stmt).all())


def asignar_tecnico(
    session: Session,
    mantenimiento_id: int,
    tecnico_id: int
) -> Mantenimiento:
    mantenimiento = session.get(
        Mantenimiento,
        mantenimiento_id
    )

    if mantenimiento is None:
        raise ValueError(
            f"No existe un mantenimiento con ID {mantenimiento_id}."
        )

    tecnico = session.get(Tecnico, tecnico_id)

    if tecnico is None:
        raise ValueError(
            f"No existe un técnico con ID {tecnico_id}."
        )

    if tecnico not in mantenimiento.tecnicos:
        mantenimiento.tecnicos.append(tecnico)

        confirmar(session)

        session.refresh(mantenimiento)

    return mantenimiento
