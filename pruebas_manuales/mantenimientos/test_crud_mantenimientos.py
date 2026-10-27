from database.db import SessionLocal
from crud.mantenimientos import (
    listar_mantenimientos,
    obtener_mantenimiento,
    listar_mantenimientos_equipo,
)


with SessionLocal() as session:
    print("=== MANTENIMIENTOS ===")

    mantenimientos = listar_mantenimientos(session)

    for mantenimiento in mantenimientos:
        print(
            f"ID: {mantenimiento.id} | "
            f"Equipo: {mantenimiento.equipo_id} | "
            f"Fecha: {mantenimiento.fecha} | "
            f"Tipo: {mantenimiento.tipo_mantenimiento}"
        )

    print("\n=== BUSCAR MANTENIMIENTO POR ID ===")

    mantenimiento = obtener_mantenimiento(session, 1)

    if mantenimiento is not None:
        print(f"ID: {mantenimiento.id}")
        print(f"Equipo: {mantenimiento.equipo.nombre}")
        print(f"Tipo: {mantenimiento.tipo_mantenimiento}")

        if mantenimiento.falla is not None:
            print(f"Falla asociada: {mantenimiento.falla.tipo_falla}")
        else:
            print("Sin falla asociada")

        print("Técnicos:")

        for tecnico in mantenimiento.tecnicos:
            print(f"- {tecnico.nombre} {tecnico.apellido}")

    else:
        print("No existe un mantenimiento con ID 1")

    print("\n=== HISTORIAL DEL EQUIPO 1 ===")

    historial = listar_mantenimientos_equipo(session, 1)

    if historial is None:
        print("No existe el equipo con ID 1")
    else:
        for mantenimiento in historial:
            print(f"- {mantenimiento.fecha} | {mantenimiento.tipo_mantenimiento}")
