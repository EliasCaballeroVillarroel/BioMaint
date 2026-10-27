from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from crud.errores import ConflictoError, DatosInvalidosError, NoEncontradoError
from crud.transacciones import confirmar
from models import Mantenimiento, Equipo, Falla, Tecnico

# Campos que definen la relación del mantenimiento con su falla.
CAMPOS_DE_LA_RELACION = {"tipo_mantenimiento", "falla_id", "fecha"}


def validar_relacion_con_falla(
    session: Session,
    equipo_id: int,
    tipo_mantenimiento: str,
    falla_id: int | None,
    fecha: date,
) -> None:
    # Solo un correctivo atiende una falla, y siempre debe indicarla.
    if tipo_mantenimiento == "Correctivo" and falla_id is None:
        raise DatosInvalidosError(
            "Un mantenimiento correctivo debe indicar la falla que atiende."
        )

    if tipo_mantenimiento != "Correctivo" and falla_id is not None:
        raise DatosInvalidosError(
            "Solo un mantenimiento correctivo puede tener una falla asociada."
        )

    if falla_id is None:
        return

    falla = session.get(Falla, falla_id)

    if falla is None:
        raise NoEncontradoError("una falla", falla_id)

    if falla.equipo_id != equipo_id:
        raise DatosInvalidosError("La falla no pertenece al equipo del mantenimiento.")

    if fecha < falla.fecha_falla:
        raise DatosInvalidosError(
            "El mantenimiento no puede ser anterior a la falla que atiende."
        )


def obtener_o_fallar(session: Session, modelo, recurso: str, registro_id: int):
    registro = session.get(modelo, registro_id)

    if registro is None:
        raise NoEncontradoError(recurso, registro_id)

    return registro


def listar_mantenimientos(session: Session) -> list[Mantenimiento]:
    # La respuesta incluye tecnico_ids: cargarlos en una sola consulta.
    stmt = (
        select(Mantenimiento)
        .options(selectinload(Mantenimiento.tecnicos))
        .order_by(Mantenimiento.id)
    )
    return list(session.scalars(stmt).all())


def obtener_mantenimiento(
    session: Session, mantenimiento_id: int
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
    resultado: str | None = None,
) -> Mantenimiento:
    equipo = obtener_o_fallar(session, Equipo, "un equipo", equipo_id)

    if equipo.dado_de_baja:
        raise ConflictoError(
            "No se pueden registrar mantenimientos en un equipo dado de baja."
        )

    validar_relacion_con_falla(
        session,
        equipo_id=equipo_id,
        tipo_mantenimiento=tipo_mantenimiento,
        falla_id=falla_id,
        fecha=fecha,
    )

    mantenimiento = Mantenimiento(
        equipo_id=equipo_id,
        falla_id=falla_id,
        fecha=fecha,
        tipo_mantenimiento=tipo_mantenimiento,
        duracion_mantenimiento=duracion_mantenimiento,
        descripcion=descripcion,
        resultado=resultado,
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
    campos_enviados: set[str] | None = None,
) -> Mantenimiento | None:
    # Se permite aunque el equipo esté dado de baja: la baja impide
    # registrar mantenimientos nuevos, no completar los existentes.
    mantenimiento = session.get(Mantenimiento, mantenimiento_id)

    if mantenimiento is None:
        return None

    valores = {
        "fecha": fecha,
        "tipo_mantenimiento": tipo_mantenimiento,
        "falla_id": falla_id,
        "duracion_mantenimiento": duracion_mantenimiento,
        "descripcion": descripcion,
        "resultado": resultado,
    }

    # Compatibilidad con llamadas anteriores al CRUD.
    if campos_enviados is None:
        campos_enviados = {
            nombre for nombre, valor in valores.items() if valor is not None
        }

    # Un resultado registrado no se puede borrar: si no, bastaría con
    # vaciarlo para poder eliminar el mantenimiento.
    if (
        mantenimiento.finalizado
        and "resultado" in campos_enviados
        and not (resultado or "").strip()
    ):
        raise ConflictoError(
            "No se puede quitar el resultado de un mantenimiento registrado."
        )

    # Validar la relación con la falla solo si cambia, sobre los
    # valores que quedarían después del cambio.
    if campos_enviados & CAMPOS_DE_LA_RELACION:

        def final(campo):
            if campo in campos_enviados:
                return valores[campo]
            return getattr(mantenimiento, campo)

        validar_relacion_con_falla(
            session,
            equipo_id=mantenimiento.equipo_id,
            tipo_mantenimiento=final("tipo_mantenimiento"),
            falla_id=final("falla_id"),
            fecha=final("fecha"),
        )

    for nombre in campos_enviados:
        if nombre in valores:
            setattr(mantenimiento, nombre, valores[nombre])

    confirmar(session)

    session.refresh(mantenimiento)
    return mantenimiento


def eliminar_mantenimiento(session: Session, mantenimiento_id: int) -> bool:
    mantenimiento = session.get(Mantenimiento, mantenimiento_id)

    if mantenimiento is None:
        return False

    # Se protege el historial: un mantenimiento con resultado
    # cargado ya ocurrió y no se borra.
    if mantenimiento.finalizado:
        raise ConflictoError(
            "No se puede eliminar un mantenimiento con resultado registrado: "
            "forma parte del historial."
        )

    # Las asignaciones de técnicos se borran con él (tabla intermedia).
    session.delete(mantenimiento)

    confirmar(session)

    return True


def listar_mantenimientos_equipo(
    session: Session, equipo_id: int
) -> list[Mantenimiento] | None:
    if session.get(Equipo, equipo_id) is None:
        return None

    stmt = (
        select(Mantenimiento)
        .options(selectinload(Mantenimiento.tecnicos))
        .where(Mantenimiento.equipo_id == equipo_id)
        .order_by(Mantenimiento.fecha.desc())
    )

    return list(session.scalars(stmt).all())


def asignar_tecnico(
    session: Session, mantenimiento_id: int, tecnico_id: int
) -> Mantenimiento:
    mantenimiento = obtener_o_fallar(
        session, Mantenimiento, "un mantenimiento", mantenimiento_id
    )
    tecnico = obtener_o_fallar(session, Tecnico, "un técnico", tecnico_id)

    # Se permite aunque el mantenimiento esté finalizado: completar
    # tarde quién participó suma información al historial, no la quita.
    if tecnico not in mantenimiento.tecnicos:
        mantenimiento.tecnicos.append(tecnico)

        confirmar(session)

        session.refresh(mantenimiento)

    return mantenimiento


def desasignar_tecnico(
    session: Session, mantenimiento_id: int, tecnico_id: int
) -> Mantenimiento:
    mantenimiento = obtener_o_fallar(
        session, Mantenimiento, "un mantenimiento", mantenimiento_id
    )
    tecnico = obtener_o_fallar(session, Tecnico, "un técnico", tecnico_id)

    # Quién hizo un mantenimiento terminado es parte del historial.
    if mantenimiento.finalizado:
        raise ConflictoError(
            "No se puede desasignar un técnico de un mantenimiento "
            "con resultado registrado: forma parte del historial."
        )

    # Idempotente, como asignar: si no estaba asignado, no hay cambios.
    if tecnico in mantenimiento.tecnicos:
        mantenimiento.tecnicos.remove(tecnico)
        confirmar(session)
        session.refresh(mantenimiento)

    return mantenimiento
