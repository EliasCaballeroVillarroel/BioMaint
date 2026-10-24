"""
from database.db import SessionLocal
from crud.ubicaciones import (
    listar_ubicaciones,
    obtener_ubicacion,
    listar_equipos_ubicacion
)


with SessionLocal() as session:
    print("=== UBICACIONES ===")

    ubicaciones = listar_ubicaciones(session)

    for ubicacion in ubicaciones:
        print(
            f"ID: {ubicacion.id} | "
            f"Clínica ID: {ubicacion.clinica_id} | "
            f"Servicio: {ubicacion.servicio} | "
            f"Sector: {ubicacion.sector}"
        )

    print("\n=== EQUIPOS DE LA UBICACIÓN 1 ===")

    ubicacion = obtener_ubicacion(session, 1)

    if ubicacion is None:
        print("No existe la ubicación con ID 1")
    else:
        equipos = listar_equipos_ubicacion(
            session,
            ubicacion.id
        )

        for equipo in equipos:
            print(
                f"- ID: {equipo.id} | "
                f"Nombre: {equipo.nombre}"
            )
"""
