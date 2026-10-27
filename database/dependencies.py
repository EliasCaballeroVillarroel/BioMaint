from collections.abc import Generator

from sqlalchemy.orm import Session

from database.db import SessionLocal


def obtener_sesion() -> Generator[Session, None, None]:
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
