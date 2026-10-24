
from database.db import SessionLocal
from crud.mantenimientos import eliminar_mantenimiento

ID_MANTENIMIENTO_PRUEBA = 34  # Reemplazar por el ID real

with SessionLocal() as session:
    if ID_MANTENIMIENTO_PRUEBA == 0:
        print("Ingresá el ID real del mantenimiento de prueba.")
    else:
        eliminado = eliminar_mantenimiento(
            session,
            ID_MANTENIMIENTO_PRUEBA
        )
        print("¿Se eliminó?", eliminado)
