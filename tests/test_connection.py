from sqlalchemy import select

from database.db import SessionLocal
from models.equipos import Equipo


with SessionLocal() as session:

    stmt = select(Equipo).where(Equipo.id == 26) #stmt es una variable que contiene la consulta que se va a ejecutar, en este caso es un select de la tabla equipos

    equipo = session.scalars(stmt) #scalars es un metodo que permite obtener los resultados de la consulta en forma de una lista de objetos, en este caso de objetos de la clase Equipo. all() es un metodo que permite obtener todos los resultados de la consulta.

    equipo.estado_actual = "EN_MANTENIMIENTO"

    session.commit() #commit es un metodo que permite guardar los cambios en la base de datos, en este caso el cambio del estado del equipo.

    print("Equipo actualizado correctamente")