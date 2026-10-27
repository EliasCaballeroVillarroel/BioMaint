from crud.ubicaciones import eliminar_ubicacion, obtener_ubicacion
from database.db import SessionLocal

# Reemplazar por el ID real de la ubicación de prueba.
ID_UBICACION_PRUEBA = 6

with SessionLocal() as session:
    if ID_UBICACION_PRUEBA == 0:
        print("Primero ingresá el ID real de la ubicación de prueba.")

    else:
        eliminada = eliminar_ubicacion(session, ID_UBICACION_PRUEBA)

        if eliminada:
            print("Ubicación de prueba eliminada.")
        else:
            print("No se eliminó. Verificá el ID y que no tenga equipos asociados.")

        ubicacion = obtener_ubicacion(session, ID_UBICACION_PRUEBA)

        print("¿Sigue existiendo?", ubicacion is not None)
