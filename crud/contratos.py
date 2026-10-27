from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from crud.errores import ConflictoError, DatosInvalidosError, NoEncontradoError
from crud.transacciones import confirmar
from models import Contrato, Equipo


def listar_contratos(session: Session) -> list[Contrato]:
    stmt = select(Contrato).order_by(Contrato.id)
    return list(session.scalars(stmt).all())


def obtener_contrato(session: Session, contrato_id: int) -> Contrato | None:
    return session.get(Contrato, contrato_id)


def crear_contrato(
    session: Session,
    equipo_id: int,
    tipo_contrato: str,
    fecha_inicio: date,
    empresa: str | None = None,
    fecha_fin: date | None = None,
) -> Contrato:
    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        raise NoEncontradoError("un equipo", equipo_id)

    if equipo.dado_de_baja:
        raise ConflictoError(
            "No se pueden registrar contratos en un equipo dado de baja."
        )

    if fecha_fin is not None and fecha_fin < fecha_inicio:
        raise DatosInvalidosError(
            "La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    contrato = Contrato(
        equipo_id=equipo_id,
        tipo_contrato=tipo_contrato,
        empresa=empresa,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
    )

    session.add(contrato)

    confirmar(session)

    session.refresh(contrato)
    return contrato


def actualizar_contrato(
    session: Session,
    contrato_id: int,
    tipo_contrato: str | None = None,
    empresa: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    campos_enviados: set[str] | None = None,
) -> Contrato | None:
    contrato = session.get(Contrato, contrato_id)

    if contrato is None:
        return None

    if contrato.cancelado:
        raise ConflictoError("No se puede modificar un contrato cancelado.")

    if campos_enviados is None:
        campos_enviados = {
            nombre
            for nombre, valor in {
                "tipo_contrato": tipo_contrato,
                "empresa": empresa,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
            }.items()
            if valor is not None
        }

    valores = {
        "tipo_contrato": tipo_contrato,
        "empresa": empresa,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
    }

    # Calcular las fechas que tendría el contrato después del cambio.
    nueva_fecha_inicio = (
        fecha_inicio if "fecha_inicio" in campos_enviados else contrato.fecha_inicio
    )

    nueva_fecha_fin = (
        fecha_fin if "fecha_fin" in campos_enviados else contrato.fecha_fin
    )

    if nueva_fecha_inicio is None:
        raise DatosInvalidosError("La fecha de inicio no puede ser nula.")

    # El inicio de un contrato que ya comenzó es historial: moverlo
    # permitiría, por ejemplo, volverlo "pendiente" y poder borrarlo.
    if (
        nueva_fecha_inicio != contrato.fecha_inicio
        and contrato.fecha_inicio <= date.today()
    ):
        raise ConflictoError(
            "No se puede cambiar la fecha de inicio de un contrato que ya comenzó."
        )

    if nueva_fecha_fin is not None and nueva_fecha_fin < nueva_fecha_inicio:
        raise DatosInvalidosError(
            "La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    # Aplicar únicamente los campos enviados.
    for nombre in campos_enviados:
        if nombre not in valores:
            raise DatosInvalidosError(f"Campo no permitido: {nombre}.")

        setattr(contrato, nombre, valores[nombre])

    confirmar(session)

    session.refresh(contrato)
    return contrato


def eliminar_contrato(session: Session, contrato_id: int) -> bool:
    contrato = session.get(Contrato, contrato_id)

    if contrato is None:
        return False

    # Se protege el historial: un contrato que ya comenzó no se borra,
    # se cancela. Solo se borran los futuros (por ejemplo, mal cargados).
    if contrato.fecha_inicio <= date.today():
        raise ConflictoError(
            "No se puede eliminar un contrato que ya comenzó: "
            "forma parte del historial. Se puede cancelar."
        )

    session.delete(contrato)

    confirmar(session)

    return True


def cancelar_contrato(session: Session, contrato_id: int) -> Contrato | None:
    contrato = session.get(Contrato, contrato_id)

    if contrato is None:
        return None

    if not contrato.cancelado:
        contrato.cancelado = True
        confirmar(session)
        session.refresh(contrato)

    return contrato


def listar_contratos_equipo(session: Session, equipo_id: int) -> list[Contrato] | None:
    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        return None

    stmt = (
        select(Contrato)
        .where(Contrato.equipo_id == equipo_id)
        .order_by(Contrato.fecha_inicio.desc())
    )

    return list(session.scalars(stmt).all())
