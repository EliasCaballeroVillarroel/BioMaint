from sqlalchemy import select
from database.db import SessionLocal
from models.equipos import Equipo
from models.ubicaciones import Ubicacion


with SessionLocal() as session:

    stmt = select(Equipo).where(Equipo.id == 1)

    equipo = session.scalar(stmt)

    print("Equipo:")
    print(equipo.nombre)

    print("\nUbicación:")
    print(equipo.ubicacion.servicio)
    print(equipo.ubicacion.sector)
    print(equipo.ubicacion.piso)
    print(equipo.ubicacion.sala)

    ubicacion = equipo.ubicacion

    for equipo in ubicacion.equipos:
        print(equipo.nombre)

    ubicacion = equipo.ubicacion

    print("\nEquipos en esta ubicación:")

    for equipo in ubicacion.equipos:
        print(
            equipo.id,
            equipo.nombre,
            equipo.marca,
            equipo.modelo
        )

