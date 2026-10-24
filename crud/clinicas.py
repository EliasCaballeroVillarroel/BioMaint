from sqlalchemy import select
from sqlalchemy.orm import Session

from crud.errores import ConflictoError
from crud.transacciones import confirmar
from models import Clinica


def listar_clinicas(
    session: Session,
    incluir_inactivas: bool = False
) -> list[Clinica]:
    stmt = select(Clinica).order_by(Clinica.id)

    if not incluir_inactivas:
        stmt = stmt.where(Clinica.activa.is_(True))

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

    confirmar(session)

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

    if not clinica.activa:
        raise ConflictoError(
            "No se puede modificar una clínica dada de baja."
        )

    if nombre is not None:
        clinica.nombre = nombre

    if direccion is not None:
        clinica.direccion = direccion

    confirmar(session)

    session.refresh(clinica)
    return clinica


def eliminar_clinica(
    session: Session,
    clinica_id: int
) -> bool:
    clinica = session.get(Clinica, clinica_id)

    if clinica is None:
        return False

    # Con ubicaciones solo se permite la baja lógica.
    if clinica.ubicaciones:
        raise ConflictoError(
            "No se puede eliminar la clínica porque tiene "
            f"{len(clinica.ubicaciones)} ubicaciones asociadas. "
            f"Para darla de baja usá POST /clinicas/{clinica_id}/baja."
        )

    session.delete(clinica)

    confirmar(session)

    return True


def cambiar_estado_clinica(
    session: Session,
    clinica_id: int,
    activa: bool
) -> Clinica | None:
    clinica = session.get(Clinica, clinica_id)

    if clinica is None:
        return None

    # La clínica y sus ubicaciones cambian juntas.
    clinica.activa = activa

    for ubicacion in clinica.ubicaciones:
        ubicacion.activa = activa

    confirmar(session)

    session.refresh(clinica)
    return clinica


def dar_de_baja_clinica(
    session: Session,
    clinica_id: int
) -> Clinica | None:
    return cambiar_estado_clinica(session, clinica_id, activa=False)


def reactivar_clinica(
    session: Session,
    clinica_id: int
) -> Clinica | None:
    return cambiar_estado_clinica(session, clinica_id, activa=True)


def listar_ubicaciones_clinica(
    session: Session,
    clinica_id: int
):
    clinica = session.get(Clinica, clinica_id)

    if clinica is None:
        return None

    return clinica.ubicaciones
