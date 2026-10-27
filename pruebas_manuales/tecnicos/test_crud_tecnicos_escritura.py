from database.db import SessionLocal
from crud.tecnicos import crear_tecnico, actualizar_tecnico, eliminar_tecnico

with SessionLocal() as session:
    tecnico_id = None

    try:
        # 1. CREACIÓN
        tecnico = crear_tecnico(
            session=session,
            nombre="TECNICO",
            apellido="PRUEBA CRUD",
            empresa="Empresa de prueba",
        )

        tecnico_id = tecnico.id

        print("=== TÉCNICO CREADO ===")
        print(f"ID: {tecnico.id}")
        print(f"Nombre: {tecnico.nombre}")
        print(f"Apellido: {tecnico.apellido}")
        print(f"Empresa: {tecnico.empresa}")

        # 2. ACTUALIZACIÓN
        tecnico_actualizado = actualizar_tecnico(
            session=session,
            tecnico_id=tecnico_id,
            nombre="TECNICO ACTUALIZADO",
            empresa="Empresa actualizada",
        )

        print("\n=== TÉCNICO ACTUALIZADO ===")

        if tecnico_actualizado is not None:
            print(f"ID: {tecnico_actualizado.id}")
            print(f"Nombre: {tecnico_actualizado.nombre}")
            print(f"Apellido: {tecnico_actualizado.apellido}")
            print(f"Empresa: {tecnico_actualizado.empresa}")
        else:
            print("No se encontró el técnico para actualizar.")

    finally:
        # 3. LIMPIEZA
        if tecnico_id is not None:
            # Por si una operación anterior dejó una transacción pendiente.
            session.rollback()

            eliminado = eliminar_tecnico(session, tecnico_id)

            print("\n=== LIMPIEZA ===")
            print(f"¿Se eliminó el técnico de prueba?: {eliminado}")
