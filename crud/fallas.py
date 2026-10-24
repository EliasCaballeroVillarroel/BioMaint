
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from crud.transacciones import confirmar
from models import Falla


def listar_fallas(session: Session) -> list[Falla]:
    stmt = select(Falla).order_by(Falla.id)
    return list(session.scalars(stmt).all())


def obtener_falla(
    session: Session,
    falla_id: int
) -> Falla | None:
    return session.get(Falla, falla_id)


def crear_falla(
    session: Session,
    equipo_id: int,
    tipo_falla: str,
    fecha_falla: date,
    descripcion_falla: str | None = None,
    fecha_resolucion: date | None = None,
    severidad: str | None = None
) -> Falla:
    falla = Falla(
        equipo_id=equipo_id,
        tipo_falla=tipo_falla,
        fecha_falla=fecha_falla,
        descripcion_falla=descripcion_falla,
        fecha_resolucion=fecha_resolucion,
        severidad=severidad
    )

    session.add(falla)

    confirmar(session)

    session.refresh(falla)
    return falla


def actualizar_falla(
    session: Session,
    falla_id: int,
    tipo_falla: str | None = None,
    descripcion_falla: str | None = None,
    fecha_falla: date | None = None,
    fecha_resolucion: date | None = None,
    severidad: str | None = None
) -> Falla | None:
    falla = session.get(Falla, falla_id)

    if falla is None:
        return None

    if tipo_falla is not None:
        falla.tipo_falla = tipo_falla

    if descripcion_falla is not None:
        falla.descripcion_falla = descripcion_falla

    if fecha_falla is not None:
        falla.fecha_falla = fecha_falla

    if fecha_resolucion is not None:
        falla.fecha_resolucion = fecha_resolucion

    if severidad is not None:
        falla.severidad = severidad

    confirmar(session)

    session.refresh(falla)
    return falla


def eliminar_falla(
    session: Session,
    falla_id: int
) -> bool:
    falla = session.get(Falla, falla_id)

    if falla is None:
        return False

    if falla.mantenimientos:
        raise ValueError(
            "No se puede eliminar la falla porque tiene mantenimientos asociados."
        )

    session.delete(falla)

    confirmar(session)

    return True


def listar_fallas_equipo(
    session: Session,
    equipo_id: int
) -> list[Falla] | None:
    from models import Equipo

    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        return None

    stmt = (
        select(Falla)
        .where(Falla.equipo_id == equipo_id)
        .order_by(Falla.fecha_falla.desc())
    )

    return list(session.scalars(stmt).all())
