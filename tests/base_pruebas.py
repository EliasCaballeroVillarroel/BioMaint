"""
Conexión exclusiva a la base de pruebas.

Vive en un módulo propio (y no en conftest.py) para que los tests puedan
importarla sin importar conftest, que pytest ya carga por su cuenta.
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

# Cargar las variables de conexión de .env
load_dotenv()

url_pruebas = URL.create(
    drivername="mysql+mysqlconnector",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    database="biomaint_test",
)

if url_pruebas.database != "biomaint_test":
    raise RuntimeError(
        "Seguridad: los tests deben usar exclusivamente biomaint_test."
    )

engine_pruebas = create_engine(
    url_pruebas,
    echo=False,
)

SesionPruebas = sessionmaker(
    bind=engine_pruebas,
    autocommit=False,
    autoflush=False,
)
