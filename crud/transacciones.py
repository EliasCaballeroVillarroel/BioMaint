from sqlalchemy.orm import Session


def confirmar(session: Session) -> None:
    # Confirma los cambios pendientes; si falla, los revierte
    # para que la sesión no quede inutilizable y relanza el error.
    try:
        session.commit()
    except Exception:
        session.rollback()
        raise
