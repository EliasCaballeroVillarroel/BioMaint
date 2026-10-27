from datetime import date

from crud.mantenimientos import (
    actualizar_mantenimiento,
    asignar_tecnico,
    crear_mantenimiento,
    obtener_mantenimiento,
)
from database.db import SessionLocal

with SessionLocal() as session:
    mantenimiento = crear_mantenimiento(
        session=session,
        equipo_id=1,
        fecha=date.today(),
        tipo_mantenimiento="PREVENTIVO",
        descripcion="Mantenimiento de prueba CRUD",
        duracion_mantenimiento=30,
        resultado="Prueba inicial",
    )

    mantenimiento_id = mantenimiento.id

    print("=== MANTENIMIENTO CREADO ===")
    print(f"ID: {mantenimiento.id}")
    print(f"Equipo: {mantenimiento.equipo_id}")
    print(f"Tipo: {mantenimiento.tipo_mantenimiento}")
    print(f"Fecha: {mantenimiento.fecha}")

    actualizado = actualizar_mantenimiento(
        session=session,
        mantenimiento_id=mantenimiento_id,
        descripcion="Descripción actualizada de prueba",
        duracion_mantenimiento=45,
    )

    print("\n=== MANTENIMIENTO ACTUALIZADO ===")

    if actualizado is not None:
        print(f"Descripción: {actualizado.descripcion}")
        print(f"Duración: {actualizado.duracion_mantenimiento} minutos")

    verificado = obtener_mantenimiento(session, mantenimiento_id)

    print("\n¿Existe en la base de datos?", verificado is not None)

    # Usamos el técnico con ID 1, que debe existir.
    asignado = asignar_tecnico(
        session=session, mantenimiento_id=mantenimiento_id, tecnico_id=1
    )

    print("\n=== TÉCNICOS ASIGNADOS ===")

    for tecnico in asignado.tecnicos:
        print(f"- {tecnico.nombre} {tecnico.apellido}")
