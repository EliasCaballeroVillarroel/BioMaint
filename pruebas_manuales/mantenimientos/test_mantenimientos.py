from sqlalchemy import select

from database.db import SessionLocal
from models import Mantenimiento

with SessionLocal() as session:
    stmt = select(Mantenimiento).limit(5)
    mantenimientos = session.scalars(stmt).all()

    for mantenimiento in mantenimientos:
        print(f"\nMantenimiento: {mantenimiento.id}")
        print(f"Tipo: {mantenimiento.tipo_mantenimiento}")
        print(f"Equipo: {mantenimiento.equipo.nombre}")

        if mantenimiento.falla is not None:
            print(f"Falla asociada: {mantenimiento.falla.tipo_falla}")
        else:
            print("Sin falla asociada")
