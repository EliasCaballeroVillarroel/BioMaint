from crud.fallas import listar_fallas, listar_fallas_equipo, obtener_falla
from database.db import SessionLocal

with SessionLocal() as session:
    print("=== FALLAS REGISTRADAS ===")

    fallas = listar_fallas(session)

    for falla in fallas:
        print(
            f"ID: {falla.id} | "
            f"Equipo: {falla.equipo_id} | "
            f"Tipo: {falla.tipo_falla} | "
            f"Fecha: {falla.fecha_falla} | "
            f"Severidad: {falla.severidad}"
        )

    print("\n=== BUSCAR FALLA POR ID ===")

    falla = obtener_falla(session, 1)

    if falla is not None:
        print(f"Falla encontrada: {falla.tipo_falla}")
        print(f"Equipo asociado: {falla.equipo.nombre}")
    else:
        print("No existe una falla con ID 1")

    print("\n=== HISTORIAL DEL EQUIPO 1 ===")

    fallas_equipo = listar_fallas_equipo(session, 1)

    if fallas_equipo is None:
        print("No existe el equipo con ID 1")
    else:
        for falla in fallas_equipo:
            print(f"- {falla.fecha_falla} | {falla.tipo_falla} | {falla.severidad}")
