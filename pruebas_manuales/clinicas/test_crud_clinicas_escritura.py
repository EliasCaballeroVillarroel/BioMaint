from crud.clinicas import actualizar_clinica, crear_clinica, obtener_clinica
from database.db import SessionLocal

with SessionLocal() as session:
    clinica = crear_clinica(
        session=session, nombre="CLINICA PRUEBA CRUD", direccion="Direccion de prueba"
    )

    clinica_id = clinica.id

    print("=== CLÍNICA CREADA ===")
    print(f"ID: {clinica.id}")
    print(f"Nombre: {clinica.nombre}")

    clinica_actualizada = actualizar_clinica(
        session=session,
        clinica_id=clinica_id,
        direccion="Direccion actualizada de prueba",
    )

    print("\n=== CLÍNICA ACTUALIZADA ===")

    if clinica_actualizada is not None:
        print(f"ID: {clinica_actualizada.id}")
        print(f"Nombre: {clinica_actualizada.nombre}")
        print(f"Dirección: {clinica_actualizada.direccion}")

    # Verificamos que siga existiendo en la base de datos.
    clinica_verificada = obtener_clinica(session, clinica_id)

    print("\n¿Existe en la base de datos?", clinica_verificada is not None)
