"""
Crea las bases de datos del proyecto y carga datos de ejemplo.

- DB_NAME (desarrollo): se crean las tablas aplicando las migraciones de
  Alembic (database/migraciones) y se cargan los datos de "database/semillas/llenado_tablas_biomaint.sql",
  normalizando los valores a los que acepta la API. También se cargan
  contratos de ejemplo usando el CRUD del proyecto.
- biomaint_test: solo se crea vacía; conftest.py la migra y
  cada test genera y limpia sus propios datos.

Uso:
    python -m database.inicializar_bases
"""

import os
import re
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine, func, inspect, select, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

from crud.contratos import cancelar_contrato, crear_contrato
from database.migrar import REVISION_INICIAL, migrar
from models import Clinica, Equipo

load_dotenv()

BASE_PRUEBAS = "biomaint_test"
ARCHIVO_LLENADO = (
    Path(__file__).resolve().parent / "semillas" / "llenado_tablas_biomaint.sql"
)

# Valores del backup -> valores que usa la API (schemas/).
NORMALIZACIONES = [
    "UPDATE equipos SET estado_actual = 'activo' WHERE estado_actual = 'ACTIVO'",
    "UPDATE equipos SET estado_actual = 'inactivo' WHERE estado_actual = 'INACTIVO'",
    "UPDATE equipos SET estado_actual = 'mantenimiento' "
    "WHERE estado_actual = 'EN_MANTENIMIENTO'",
    "UPDATE mantenimientos SET tipo_mantenimiento = 'Preventivo' "
    "WHERE tipo_mantenimiento = 'PREVENTIVO'",
    "UPDATE mantenimientos SET tipo_mantenimiento = 'Predictivo' "
    "WHERE tipo_mantenimiento = 'PREDICTIVO'",
    "UPDATE mantenimientos SET tipo_mantenimiento = 'Correctivo' "
    "WHERE tipo_mantenimiento = 'CORRECTIVO'",
    # Mismas sentencias que la migración 9dde320bbb20 (se copian en vez
    # de importarse: una migración es una foto fija y no debe cambiar).
    "UPDATE fallas SET severidad = LOWER(TRIM(severidad)) "
    "WHERE severidad IS NOT NULL",
    "UPDATE fallas SET severidad = 'critica' WHERE severidad = 'crítica'",
]

# (numero_serie del equipo, tipo, empresa, inicio, fin, cancelado).
# El estado se calcula con las fechas: hoy hay activos, vencidos y uno pendiente.
CONTRATOS_EJEMPLO = [
    ("SN-RES-001", "Mantenimiento integral", "Siemens", date(2024, 1, 1), date(2026, 12, 31), False),
    ("SN-TC-001", "Mantenimiento integral", "Siemens", date(2023, 5, 1), date(2025, 4, 30), False),
    ("SN-TC-001", "Mantenimiento integral", "Siemens", date(2025, 5, 1), date(2027, 4, 30), False),
    ("SN-HEM-001", "Full risk", "Siemens", date(2024, 7, 1), date(2027, 6, 30), False),
    ("SN-HEM-002", "Preventivo", "Medrad", date(2024, 1, 1), date(2024, 12, 31), False),
    ("SN-RAD-002", "Preventivo", "GE HealthCare", date(2025, 3, 1), date(2026, 2, 28), True),
    ("SN-RAD-003", "Mantenimiento integral", "Siemens", date(2026, 11, 1), None, False),
]


def url_servidor(base: str | None = None) -> URL:
    return URL.create(
        drivername="mysql+mysqlconnector",
        username=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        database=base,
    )


def crear_base(nombre: str) -> None:
    engine = create_engine(url_servidor())
    with engine.begin() as conexion:
        conexion.execute(
            text(
                f"CREATE DATABASE IF NOT EXISTS `{nombre}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        )
    engine.dispose()


def leer_inserts(archivo: Path) -> list[str]:
    contenido = archivo.read_text(encoding="utf-8")

    # El backup tiene los INSERT dentro de un bloque /* ... */.
    contenido = contenido.replace("/*", "").replace("*/", "")
    # Quitamos comentarios de línea (ningún dato contiene "--").
    contenido = re.sub(r"--[^\n]*", "", contenido)

    sentencias = [s.strip() for s in contenido.split(";")]
    return [s for s in sentencias if s.upper().startswith("INSERT")]


def cargar_datos_desarrollo(nombre: str) -> None:
    engine = create_engine(url_servidor(nombre))

    # Una base creada antes de Alembic tiene tablas pero no su versión.
    tablas = inspect(engine).get_table_names()
    if tablas and "alembic_version" not in tablas:
        raise RuntimeError(
            f"'{nombre}' fue creada sin migraciones. Marcala con la "
            "revisión que corresponde a su esquema y aplicá el resto:\n"
            f"  - sin la columna clinicas.activa: alembic stamp {REVISION_INICIAL}"
            " && alembic upgrade head\n"
            "  - con la columna clinicas.activa: alembic stamp head\n"
            "Después verificá con: alembic check"
        )

    migrar(url_servidor(nombre))
    Sesion = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    with Sesion() as session:
        if session.scalar(select(func.count()).select_from(Clinica)):
            print(f"'{nombre}' ya tiene datos: no se carga nada.")
            return

        try:
            for sentencia in leer_inserts(ARCHIVO_LLENADO):
                session.execute(text(sentencia))
            for sentencia in NORMALIZACIONES:
                session.execute(text(sentencia))
            session.commit()
        except Exception:
            session.rollback()
            raise

        for numero_serie, tipo, empresa, inicio, fin, cancelado in CONTRATOS_EJEMPLO:
            equipo = session.scalar(
                select(Equipo).where(Equipo.numero_serie == numero_serie)
            )
            contrato = crear_contrato(
                session,
                equipo_id=equipo.id,
                tipo_contrato=tipo,
                fecha_inicio=inicio,
                empresa=empresa,
                fecha_fin=fin,
            )
            if cancelado:
                cancelar_contrato(session, contrato.id)

    engine.dispose()


def main() -> None:
    base_desarrollo = os.getenv("DB_NAME")

    if base_desarrollo == BASE_PRUEBAS:
        raise RuntimeError("DB_NAME no puede ser la base de pruebas.")

    crear_base(base_desarrollo)
    cargar_datos_desarrollo(base_desarrollo)
    crear_base(BASE_PRUEBAS)
    print(f"Bases '{base_desarrollo}' y '{BASE_PRUEBAS}' listas.")


if __name__ == "__main__":
    main()
