from sqlalchemy import select

from crud.ubicaciones import actualizar_ubicacion, crear_ubicacion, obtener_ubicacion
from database.db import SessionLocal
from models import Clinica

with SessionLocal() as session:
    clinica = session.scalar(select(Clinica).order_by(Clinica.id))

    if clinica is None:
        print("No hay clínicas registradas para la prueba.")

    else:
        ubicacion = crear_ubicacion(
            session=session,
            clinica_id=clinica.id,
            servicio="Servicio de prueba CRUD",
            sector="Sector de prueba",
            piso="99",
            sala="TEST",
        )

        ubicacion_id = ubicacion.id

        print("=== UBICACIÓN CREADA ===")
        print(f"ID: {ubicacion.id}")
        print(f"Clínica: {clinica.nombre}")
        print(f"Servicio: {ubicacion.servicio}")

        actualizada = actualizar_ubicacion(
            session=session,
            ubicacion_id=ubicacion_id,
            servicio="Servicio actualizado CRUD",
        )

        print("\n=== UBICACIÓN ACTUALIZADA ===")

        if actualizada is not None:
            print(f"ID: {actualizada.id}")
            print(f"Servicio: {actualizada.servicio}")

        verificada = obtener_ubicacion(session, ubicacion_id)

        print("\n¿Existe en la base de datos?", verificada is not None)
