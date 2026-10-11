
from datetime import date, timedelta

from database.db import SessionLocal
from crud.contratos import (
    crear_contrato,
    actualizar_contrato,
    eliminar_contrato
)

with SessionLocal() as session:
    contrato_id = None

    try:
        # 1. CREACIÓN
        contrato = crear_contrato(
            session=session,
            equipo_id=1,
            tipo_contrato="CONTRATO DE PRUEBA CRUD",
            fecha_inicio=date.today(),
            estado="Activo",
            empresa="Empresa de prueba",
            fecha_fin=date.today() + timedelta(days=365)
        )

        contrato_id = contrato.id

        print("=== CONTRATO CREADO ===")
        print(f"ID: {contrato.id}")
        print(f"Equipo: {contrato.equipo_id}")
        print(f"Tipo: {contrato.tipo_contrato}")
        print(f"Empresa: {contrato.empresa}")
        print(f"Inicio: {contrato.fecha_inicio}")
        print(f"Fin: {contrato.fecha_fin}")
        print(f"Estado: {contrato.estado}")

        # 2. ACTUALIZACIÓN
        contrato_actualizado = actualizar_contrato(
            session=session,
            contrato_id=contrato_id,
            tipo_contrato="CONTRATO ACTUALIZADO CRUD",
            empresa="Empresa actualizada",
            estado="Finalizado"
        )

        print("\n=== CONTRATO ACTUALIZADO ===")

        if contrato_actualizado is not None:
            print(f"ID: {contrato_actualizado.id}")
            print(f"Tipo: {contrato_actualizado.tipo_contrato}")
            print(f"Empresa: {contrato_actualizado.empresa}")
            print(f"Estado: {contrato_actualizado.estado}")
        else:
            print("No se encontró el contrato para actualizar.")

    finally:
        # 3. LIMPIEZA
        if contrato_id is not None:
            session.rollback()

            eliminado = eliminar_contrato(
                session,
                contrato_id
            )

            print("\n=== LIMPIEZA ===")
            print(f"¿Se eliminó el contrato de prueba?: {eliminado}")
