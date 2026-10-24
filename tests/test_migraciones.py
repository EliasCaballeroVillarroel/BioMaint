from alembic import command
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext
from sqlalchemy import inspect, text

from base_pruebas import engine_pruebas, url_pruebas
from database.base import Base
from database.migrar import REVISION_INICIAL, config_alembic, migrar


def diferencias_con_modelos():
    with engine_pruebas.connect() as conexion:
        contexto = MigrationContext.configure(conexion)
        return compare_metadata(contexto, Base.metadata)


def reconstruir_base_vacia():
    # Volver al estado con el que arranca la suite (ver conftest.py).
    Base.metadata.drop_all(bind=engine_pruebas)
    with engine_pruebas.begin() as conexion:
        conexion.execute(text("DROP TABLE IF EXISTS alembic_version"))
    migrar(url_pruebas)


def columnas(tabla):
    return {c["name"] for c in inspect(engine_pruebas).get_columns(tabla)}


def test_migraciones_coinciden_con_los_modelos():
    # Si falla, se cambió un modelo sin crear su migración:
    # alembic revision --autogenerate -m "descripcion del cambio"
    assert diferencias_con_modelos() == []


def test_migraciones_se_pueden_revertir_y_reaplicar():
    config = config_alembic(url_pruebas)

    try:
        command.downgrade(config, "base")
        tablas = set(inspect(engine_pruebas).get_table_names())
        assert tablas == {"alembic_version"}
    finally:
        # Dejar la base en la última versión aunque falle el downgrade,
        # para no romper el resto de la suite.
        command.upgrade(config, "head")

    tablas = set(inspect(engine_pruebas).get_table_names())
    assert set(Base.metadata.tables) <= tablas
    assert diferencias_con_modelos() == []


def test_base_creada_sin_alembic_se_actualiza_sin_perder_datos():
    # Simula una base anterior a Alembic (creada con create_all, sin
    # baja lógica ni alembic_version) y sigue los pasos que indica
    # database/inicializar_bases.py para ponerla al día.
    config = config_alembic(url_pruebas)

    try:
        command.downgrade(config, REVISION_INICIAL)
        with engine_pruebas.begin() as conexion:
            conexion.execute(text("DROP TABLE alembic_version"))
            clinica_id = conexion.execute(
                text("INSERT INTO clinicas (nombre) VALUES ('Clinica vieja')")
            ).lastrowid
            conexion.execute(
                text(
                    "INSERT INTO ubicaciones (clinica_id, servicio) "
                    "VALUES (:clinica_id, 'Servicio viejo')"
                ),
                {"clinica_id": clinica_id},
            )
        assert "activa" not in columnas("clinicas")

        command.stamp(config, REVISION_INICIAL)
        command.upgrade(config, "head")

        assert diferencias_con_modelos() == []
        with engine_pruebas.connect() as conexion:
            clinica = conexion.execute(
                text("SELECT nombre, activa FROM clinicas WHERE id = :id"),
                {"id": clinica_id},
            ).one()
            ubicacion_activa = conexion.execute(
                text("SELECT activa FROM ubicaciones WHERE clinica_id = :id"),
                {"id": clinica_id},
            ).scalar_one()

        # Los datos previos se conservan y quedan activos.
        assert clinica.nombre == "Clinica vieja"
        assert clinica.activa
        assert ubicacion_activa
    finally:
        reconstruir_base_vacia()
