from sqlalchemy import select

from database.db import SessionLocal
from models.equipos import Equipo

with SessionLocal() as session:
    stmt = select(Equipo).where(Equipo.id == 26)

    equipo = session.scalar(stmt)

    if equipo is None:
        print("No se encontró el equipo")
    else:
        session.delete(equipo)

        session.commit()

        print("Equipo eliminado correctamente")
