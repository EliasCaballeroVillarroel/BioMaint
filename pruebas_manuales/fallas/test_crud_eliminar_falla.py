from database.db import SessionLocal
from crud.fallas import eliminar_falla, obtener_falla


# Reemplazar por el ID real obtenido al crear la falla de prueba.
ID_FALLA_PRUEBA = 21

with SessionLocal() as session:
    if ID_FALLA_PRUEBA == 0:
        print("Ingresá el ID real de la falla de prueba.")

    else:
        eliminada = eliminar_falla(session, ID_FALLA_PRUEBA)

        print("¿Se eliminó?", eliminada)

        falla = obtener_falla(session, ID_FALLA_PRUEBA)

        print("¿Sigue existiendo?", falla is not None)
