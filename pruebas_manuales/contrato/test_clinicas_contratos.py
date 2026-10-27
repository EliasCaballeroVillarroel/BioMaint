from sqlalchemy import select

from database.db import SessionLocal
from models import Clinica, Contrato


with SessionLocal() as session:
    print("=== CLÍNICAS ===")

    stmt_clinicas = select(Clinica)
    clinicas = session.scalars(stmt_clinicas).all()

    for clinica in clinicas:
        print(f"\nClínica: {clinica.nombre}")
        print(f"Dirección: {clinica.direccion}")

        for ubicacion in clinica.ubicaciones:
            print(f"- {ubicacion.servicio} | Sector: {ubicacion.sector}")

    print("\n=== CONTRATOS ===")

    stmt_contratos = select(Contrato).limit(5)
    contratos = session.scalars(stmt_contratos).all()

    for contrato in contratos:
        print(f"\nContrato: {contrato.id}")
        print(f"Tipo: {contrato.tipo_contrato}")
        print(f"Empresa: {contrato.empresa}")
        print(f"Equipo: {contrato.equipo.nombre}")
