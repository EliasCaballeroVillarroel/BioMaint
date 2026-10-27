from datetime import date

from database.db import SessionLocal
from models.equipos import Equipo

equipo = Equipo(
    ubicacion_id=1,
    nombre="Ecografo",
    tipo="Ecografia",
    modelo="LOGIQ P9",
    marca="GE Healthcare",
    numero_serie="SN-ECO-023",
    fecha_adquisicion=date(2026, 10, 2),
    fecha_instalacion=date(2026, 10, 5),
    estado_actual="ACTIVO",
)

with SessionLocal() as session:
    session.add(equipo)

    session.commit()

    session.refresh(equipo)

    print("Equipo creado correctamente")
    print("ID:", equipo.id)
    print("Nombre:", equipo.nombre)
    print("Serie:", equipo.numero_serie)
