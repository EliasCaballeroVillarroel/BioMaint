from database.db import SessionLocal
from crud.contratos import listar_contratos, obtener_contrato, listar_contratos_equipo

with SessionLocal() as session:
    print("=== CONTRATOS ===")

    contratos = listar_contratos(session)

    if not contratos:
        print("Todavía no hay contratos registrados.")

    for contrato in contratos:
        print(
            f"ID: {contrato.id} | "
            f"Equipo: {contrato.equipo_id} | "
            f"Tipo: {contrato.tipo_contrato} | "
            f"Empresa: {contrato.empresa} | "
            f"Inicio: {contrato.fecha_inicio} | "
            f"Fin: {contrato.fecha_fin} | "
            f"Estado: {contrato.estado}"
        )

    print("\n=== BUSCAR CONTRATO POR ID ===")

    contrato = obtener_contrato(session, 1)

    if contrato is None:
        print("No existe un contrato con ID 1.")
    else:
        print(f"Contrato {contrato.id} asociado al equipo {contrato.equipo_id}")

    print("\n=== CONTRATOS DEL EQUIPO 1 ===")

    contratos_equipo = listar_contratos_equipo(session, 1)

    if contratos_equipo is None:
        print("No existe el equipo con ID 1.")
    elif not contratos_equipo:
        print("El equipo 1 no tiene contratos registrados.")
    else:
        for contrato in contratos_equipo:
            print(
                f"Contrato {contrato.id} | "
                f"{contrato.tipo_contrato} | "
                f"Estado: {contrato.estado}"
            )
