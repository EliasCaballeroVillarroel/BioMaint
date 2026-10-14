
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from models import Contrato, Equipo


def listar_contratos(session: Session) -> list[Contrato]:
    stmt = select(Contrato).order_by(Contrato.id)
    return list(session.scalars(stmt).all())


def obtener_contrato(
    session: Session,
    contrato_id: int
) -> Contrato | None:
    return session.get(Contrato, contrato_id)


def crear_contrato(
    session: Session,
    equipo_id: int,
    tipo_contrato: str,
    fecha_inicio: date,
    estado: str,
    empresa: str | None = None,
    fecha_fin: date | None = None
) -> Contrato:
    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        raise ValueError(
            f"No existe un equipo con ID {equipo_id}."
        )

    if fecha_fin is not None and fecha_fin < fecha_inicio:
        raise ValueError(
            "La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    contrato = Contrato(
        equipo_id=equipo_id,
        tipo_contrato=tipo_contrato,
        empresa=empresa,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado=estado
    )

    session.add(contrato)
    session.commit()
    session.refresh(contrato)

    return contrato


def actualizar_contrato(
    session: Session,
    contrato_id: int,
    tipo_contrato: str | None = None,
    empresa: str | None = None,
    fecha_inicio: date | None = None,
    fecha_fin: date | None = None,
    estado: str | None = None,
    campos_enviados: set[str] | None = None,
) -> Contrato | None:
    contrato = session.get(Contrato, contrato_id)

    if contrato is None:
        return None

    if campos_enviados is None:
        campos_enviados = {
            nombre
            for nombre, valor in {
                "tipo_contrato": tipo_contrato,
                "empresa": empresa,
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "estado": estado,
            }.items()
            if valor is not None
        }

    valores = {
        "tipo_contrato": tipo_contrato,
        "empresa": empresa,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "estado": estado,
    }

    # Calcular las fechas que tendría el contrato después del cambio.
    nueva_fecha_inicio = (
        valores["fecha_inicio"]
        if "fecha_inicio" in campos_enviados
        else contrato.fecha_inicio
    )

    nueva_fecha_fin = (
        valores["fecha_fin"]
        if "fecha_fin" in campos_enviados
        else contrato.fecha_fin
    )

    if nueva_fecha_inicio is None:
        raise ValueError("La fecha de inicio no puede ser null.")

    if (
        nueva_fecha_fin is not None
        and nueva_fecha_fin < nueva_fecha_inicio
    ):
        raise ValueError(
            "La fecha de fin no puede ser anterior a la fecha de inicio."
        )

    # Aplicar únicamente los campos enviados.
    for nombre in campos_enviados:
        if nombre not in valores:
            raise ValueError(f"Campo no permitido: {nombre}")

        setattr(contrato, nombre, valores[nombre])

    session.commit()
    session.refresh(contrato)

    return contrato



def eliminar_contrato(
    session: Session,
    contrato_id: int
) -> bool:
    contrato = session.get(Contrato, contrato_id)

    if contrato is None:
        return False

    session.delete(contrato)
    session.commit()

    return True


def listar_contratos_equipo(
    session: Session,
    equipo_id: int
) -> list[Contrato] | None:
    equipo = session.get(Equipo, equipo_id)

    if equipo is None:
        return None

    stmt = (
        select(Contrato)
        .where(Contrato.equipo_id == equipo_id)
        .order_by(Contrato.fecha_inicio.desc())
    )

    return list(session.scalars(stmt).all())
