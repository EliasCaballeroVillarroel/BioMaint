"""
from database.db import SessionLocal
from crud.equipos import listar_equipos, obtener_equipo


with SessionLocal() as session:
    print("=== LISTA DE EQUIPOS ===")

    equipos = listar_equipos(session)

    for equipo in equipos:
        print(
            f"ID: {equipo.id} | "
            f"Nombre: {equipo.nombre} | "
            f"Estado: {equipo.estado_actual}"
        )

    print("\n=== BUSCAR EQUIPO POR ID ===")

    equipo = obtener_equipo(session, 1)

    if equipo is not None:
        print(f"Encontrado: {equipo.nombre}")
    else:
        print("No existe un equipo con ese ID")


from database.db import SessionLocal
from crud.equipos import crear_equipo


with SessionLocal() as session:
    equipo = crear_equipo(
        session=session,
        nombre="EQUIPO DE PRUEBA CRUD",
        ubicacion_id=1,
        estado_actual="ACTIVO",
        tipo="Prueba"
    )

    print(f"Equipo creado correctamente")
    print(f"ID: {equipo.id}")
    print(f"Nombre: {equipo.nombre}")

from database.db import SessionLocal
from crud.equipos import actualizar_equipo


with SessionLocal() as session:
    equipo = actualizar_equipo(
        session=session,
        equipo_id=1,
        estado_actual="EN_MANTENIMIENTO"
    )

    if equipo is None:
        print("No existe un equipo con ese ID")
    else:
        print("Equipo actualizado correctamente")
        print(f"ID: {equipo.id}")
        print(f"Nombre: {equipo.nombre}")
        print(f"Estado: {equipo.estado_actual}")
"""

from crud.equipos import eliminar_equipo, obtener_equipo
from database.db import SessionLocal

# Reemplazar por el ID del equipo de prueba creado anteriormente.
ID_EQUIPO_PRUEBA = 26

with SessionLocal() as session:
    eliminado = eliminar_equipo(session, ID_EQUIPO_PRUEBA)

    if eliminado:
        print("Equipo de prueba eliminado correctamente")
    else:
        print("No se encontró el equipo de prueba")

    equipo = obtener_equipo(session, ID_EQUIPO_PRUEBA)

    print(f"¿Sigue existiendo? {equipo is not None}")
