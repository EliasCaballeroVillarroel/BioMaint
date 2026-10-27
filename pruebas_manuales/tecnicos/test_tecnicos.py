from sqlalchemy import select

from database.db import SessionLocal
from models import (
    Equipo,
    Ubicacion,
    Falla,
    Mantenimiento,
    Tecnico,
)


with SessionLocal() as session:
    stmt = select(Mantenimiento).limit(5)
    mantenimientos = session.scalars(stmt).all()

    for mantenimiento in mantenimientos:
        print(f"\nMantenimiento: {mantenimiento.id}")
        print(f"Tipo: {mantenimiento.tipo_mantenimiento}")
        print("Técnicos:")

        for tecnico in mantenimiento.tecnicos:
            print(f"- {tecnico.nombre} {tecnico.apellido}")
