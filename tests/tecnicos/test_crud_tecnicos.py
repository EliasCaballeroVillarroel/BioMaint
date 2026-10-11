
from database.db import SessionLocal
from crud.tecnicos import (
    listar_tecnicos,
    obtener_tecnico,
    listar_mantenimientos_tecnico
)


with SessionLocal() as session:
    print("=== TÉCNICOS ===")

    tecnicos = listar_tecnicos(session)

    for tecnico in tecnicos:
        print(
            f"ID: {tecnico.id} | "
            f"Nombre: {tecnico.nombre} {tecnico.apellido} | "
            f"Empresa: {tecnico.empresa}"
        )

    print("\n=== BUSCAR TÉCNICO POR ID ===")

    tecnico = obtener_tecnico(session, 1)

    if tecnico is None:
        print("No existe el técnico con ID 1")
    else:
        print(f"Encontrado: {tecnico.nombre} {tecnico.apellido}")

        mantenimientos = listar_mantenimientos_tecnico(
            session,
            tecnico.id
        )

        print("\nMantenimientos asociados:")

        for mantenimiento in mantenimientos:
            print(
                f"- ID: {mantenimiento.id} | "
                f"Fecha: {mantenimiento.fecha} | "
                f"Equipo: {mantenimiento.equipo_id}"
            )
