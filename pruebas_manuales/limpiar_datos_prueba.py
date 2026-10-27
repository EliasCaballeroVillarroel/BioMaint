from crud.clinicas import eliminar_clinica
from crud.equipos import eliminar_equipo
from database.db import SessionLocal
from models import Clinica, Equipo

with SessionLocal() as session:
    # 1. Limpiar clínica de prueba
    clinica = session.get(Clinica, 3)

    print("=== CLÍNICA DE PRUEBA ===")

    if clinica is None:
        print("La clínica ID 3 ya no existe.")
    elif clinica.nombre != "CLINICA PRUEBA CRUD":
        print("No se elimina: el ID 3 no corresponde a la clínica de prueba.")
    elif clinica.ubicaciones:
        print(
            "No se elimina: la clínica tiene ubicaciones asociadas. "
            "Hay que revisarlas primero."
        )
    else:
        eliminada = eliminar_clinica(session, 3)
        print(f"¿Se eliminó la clínica?: {eliminada}")

    # 2. Limpiar equipo de prueba
    equipo = session.get(Equipo, 27)

    print("\n=== EQUIPO DE PRUEBA ===")

    if equipo is None:
        print("El equipo ID 27 ya no existe.")
    elif equipo.nombre != "EQUIPO DE PRUEBA CRUD":
        print("No se elimina: el ID 27 no corresponde al equipo de prueba.")
    elif equipo.fallas or equipo.mantenimientos or equipo.contratos:
        print(
            "No se elimina: el equipo tiene fallas, mantenimientos "
            "o contratos asociados. Hay que revisarlos primero."
        )
    else:
        eliminado = eliminar_equipo(session, 27)
        print(f"¿Se eliminó el equipo?: {eliminado}")
