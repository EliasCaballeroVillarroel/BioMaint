from sqlalchemy import select

from database.db import SessionLocal
from models import Equipo, Ubicacion, Falla


with SessionLocal() as session:
    stmt = select(Equipo).where(Equipo.id == 1)
    equipo = session.scalar(stmt)

    if equipo is None:
        print("No se encontró el equipo")
    else:
        print(f"Equipo: {equipo.nombre}")
        print("\nFallas registradas:")

        for falla in equipo.fallas:
            print(falla.id, falla.tipo_falla, falla.fecha_falla, falla.severidad)
