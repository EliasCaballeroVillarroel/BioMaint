
from database.db import SessionLocal
from crud.clinicas import (
    listar_clinicas,
    obtener_clinica,
    listar_ubicaciones_clinica
)


with SessionLocal() as session:
    print("=== CLÍNICAS ===")

    clinicas = listar_clinicas(session)

    for clinica in clinicas:
        print(
            f"ID: {clinica.id} | "
            f"Nombre: {clinica.nombre} | "
            f"Dirección: {clinica.direccion}"
        )

    print("\n=== BUSCAR CLÍNICA POR ID ===")

    clinica = obtener_clinica(session, 1)

    if clinica is not None:
        print(f"Encontrada: {clinica.nombre}")

        ubicaciones = listar_ubicaciones_clinica(
            session,
            clinica.id
        )

        for ubicacion in ubicaciones:
            print(
                f"- {ubicacion.servicio} | "
                f"Sector: {ubicacion.sector}"
            )
    else:
        print("No existe la clínica con ID 1")
