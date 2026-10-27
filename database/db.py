import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# SQLAlchemy trabaja con ORM Object-Relational Mapping, que permite mapear las tablas de la base de datos a clases de Python y viceversa.
# Esto facilita la interacción con la base de datos utilizando objetos en lugar de escribir consultas SQL directamente.

load_dotenv()

DATABASE_URL = (
    f"mysql+mysqlconnector://"
    f"{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
)
# Engine administra las conexiones
engine = create_engine(
    DATABASE_URL,
    echo=False,  # Hace que SQL muestre en la terminal las consultas que hace
    # Mas adelante lo paso a false
)
# SessionLocal es una clase que se usa como una fabrica de sesiones
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
