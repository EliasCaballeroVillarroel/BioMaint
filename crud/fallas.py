from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from crud.errores import ConflictoError, DatosInvalidosError, NoEncontradoError
from crud.transacciones import confirmar
from models import Equipo, Falla


def listar_fallas(session: Session) -> list[Falla]:
    stmt = select(Falla).order_by(Falla.id)
    return list(session.scalars(stmt).all())


def obtener_falla(session: Session, falla_id: int) -> Falla | None:
    return session.get(Falla, falla_id)


def crear_falla(
    session: Session,
    equipo_id: int,
    tipo_falla: str,
    fecha_falla: date,
    descripcion_falla: str | None = None,
    fecha_resolucion: date | None = None,
    severidad: str | None = None,
) -> Falla:
    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        raise NoEncontradoError("un equipo", equipo_id)

    if equipo.dado_de_baja:
        raise ConflictoError("No se pueden registrar fallas en un equipo dado de baja.")

    falla = Falla(
        equipo_id=equipo_id,
        tipo_falla=tipo_falla,
        fecha_falla=fecha_falla,
        descripcion_falla=descripcion_falla,
        fecha_resolucion=fecha_resolucion,
        severidad=severidad,
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
    severidad: str | None = None,
) -> Falla | None:
    falla = session.get(Falla, falla_id)

    if falla is None:
        return None

    # Una falla resuelta es historial: si el equipo vuelve a fallar,
    # se registra una falla nueva. Sí se puede resolver una abierta
    # aunque el equipo ya esté dado de baja.
    if falla.resuelta:
        raise ConflictoError(
            "No se puede modificar una falla resuelta: si el equipo "
            "volvió a fallar, registrá una falla nueva."
        )

    # Validar las fechas que quedarían después del cambio.
    fecha_falla_final = fecha_falla or falla.fecha_falla
    fecha_resolucion_final = fecha_resolucion or falla.fecha_resolucion

    if (
        fecha_resolucion_final is not None
        and fecha_resolucion_final < fecha_falla_final
    ):
        raise DatosInvalidosError(
            "La fecha de resolución no puede ser anterior a la fecha de la falla."
        )

    # Un mantenimiento no puede ser anterior a la falla que atiende.
    if any(
        mantenimiento.fecha < fecha_falla_final
        for mantenimiento in falla.mantenimientos
    ):
        raise DatosInvalidosError(
            "La fecha de la falla no puede ser posterior a la de sus mantenimientos."
        )

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


def eliminar_falla(session: Session, falla_id: int) -> bool:
    falla = session.get(Falla, falla_id)

    if falla is None:
        return False

    # Se protege el historial: solo se borran fallas abiertas
    # y sin mantenimientos (por ejemplo, una carga errónea).
    if falla.resuelta:
        raise ConflictoError(
            "No se puede eliminar una falla resuelta: forma parte del historial."
        )

    if falla.mantenimientos:
        raise ConflictoError(
            "No se puede eliminar la falla porque tiene mantenimientos asociados."
        )

    session.delete(falla)

    confirmar(session)

    return True


def listar_fallas_equipo(session: Session, equipo_id: int) -> list[Falla] | None:
    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        return None

    stmt = (
        select(Falla)
        .where(Falla.equipo_id == equipo_id)
        .order_by(Falla.fecha_falla.desc())
    )

    return list(session.scalars(stmt).all())
