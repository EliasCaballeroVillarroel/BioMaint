from datetime import date

from crud.fallas import actualizar_falla, crear_falla, obtener_falla
from database.db import SessionLocal

with SessionLocal() as session:
    falla = crear_falla(
        session=session,
        equipo_id=1,
        tipo_falla="FALLA DE PRUEBA CRUD",
        fecha_falla=date.today(),
        descripcion_falla="Registro temporal para probar el CRUD",
        severidad="BAJA",
    )

    falla_id = falla.id

    print("=== FALLA CREADA ===")
    print(f"ID: {falla.id}")
    print(f"Equipo: {falla.equipo_id}")
    print(f"Tipo: {falla.tipo_falla}")
    print(f"Fecha: {falla.fecha_falla}")

    falla_actualizada = actualizar_falla(
        session=session,
        falla_id=falla_id,
        descripcion_falla="Descripción actualizada de prueba",
    )

    print("\n=== FALLA ACTUALIZADA ===")

    if falla_actualizada is not None:
        print(f"ID: {falla_actualizada.id}")
        print(f"Tipo: {falla_actualizada.tipo_falla}")
        print(f"Descripción: {falla_actualizada.descripcion_falla}")

    verificada = obtener_falla(session, falla_id)

    print("\n¿Existe en la base de datos?", verificada is not None)
