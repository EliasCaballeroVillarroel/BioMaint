from sqlalchemy import select

from database.db import SessionLocal
from models import Clinica, Ubicacion, Equipo, Falla, Mantenimiento, Tecnico, Contrato


with SessionLocal() as session:
    print("=== CLÍNICAS DE PRUEBA ===")
    stmt = select(Clinica).where(Clinica.nombre == "CLINICA PRUEBA CRUD")
    for registro in session.scalars(stmt):
        print(registro.id, registro.nombre, registro.direccion)

    print("\n=== UBICACIONES DE PRUEBA ===")
    stmt = select(Ubicacion).where(Ubicacion.servicio == "Servicio actualizado CRUD")
    for registro in session.scalars(stmt):
        print(
            registro.id,
            registro.servicio,
            registro.sector,
            registro.piso,
            registro.sala,
        )

    print("\n=== EQUIPOS DE PRUEBA ===")
    stmt = select(Equipo).where(Equipo.nombre.like("%PRUEBA CRUD%"))
    for registro in session.scalars(stmt):
        print(registro.id, registro.nombre, registro.ubicacion_id)

    print("\n=== FALLAS DE PRUEBA ===")
    stmt = select(Falla).where(Falla.tipo_falla == "FALLA DE PRUEBA CRUD")
    for registro in session.scalars(stmt):
        print(registro.id, registro.tipo_falla, registro.equipo_id)

    print("\n=== MANTENIMIENTOS DE PRUEBA ===")
    stmt = select(Mantenimiento).where(Mantenimiento.descripcion.like("%prueba CRUD%"))
    for registro in session.scalars(stmt):
        print(registro.id, registro.descripcion, registro.equipo_id, registro.falla_id)

    print("\n=== TÉCNICOS DE PRUEBA ===")
    stmt = select(Tecnico).where(Tecnico.apellido == "PRUEBA CRUD")
    for registro in session.scalars(stmt):
        print(registro.id, registro.nombre, registro.apellido)

    print("\n=== CONTRATOS DE PRUEBA ===")
    stmt = select(Contrato).where(Contrato.tipo_contrato.like("%PRUEBA CRUD%"))
    for registro in session.scalars(stmt):
        print(registro.id, registro.tipo_contrato, registro.equipo_id)
