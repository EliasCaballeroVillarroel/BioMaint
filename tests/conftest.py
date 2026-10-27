import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete, select, text
from sqlalchemy.orm import Session

from base_pruebas import SesionPruebas, engine_pruebas, url_pruebas
from database.base import Base
from database.dependencies import obtener_sesion
from database.migrar import migrar
from main import app
from models import (
    Clinica,
    Ubicacion,
    Equipo,
    Falla,
    Mantenimiento,
    Contrato,
    Tecnico,
    mantenimiento_tecnicos,
)


@pytest.fixture(scope="session", autouse=True)
def preparar_base_pruebas():
    # Partir de una base vacía y construir el esquema con las
    # migraciones, igual que en desarrollo. Solo afecta a biomaint_test.
    Base.metadata.drop_all(bind=engine_pruebas)
    with engine_pruebas.begin() as conexion:
        conexion.execute(text("DROP TABLE IF EXISTS alembic_version"))

    migrar(url_pruebas)
    yield
    engine_pruebas.dispose()


@pytest.fixture
def cliente():
    def obtener_sesion_pruebas():
        with SesionPruebas() as session:
            yield session

    # Guardar cualquier override previo.
    override_anterior = app.dependency_overrides.get(obtener_sesion)
    app.dependency_overrides[obtener_sesion] = obtener_sesion_pruebas

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Restaurar la configuración previa.
        if override_anterior is not None:
            app.dependency_overrides[obtener_sesion] = override_anterior
        else:
            app.dependency_overrides.pop(obtener_sesion, None)


def limpiar_clinicas(clinica_ids):
    # Elimina las clínicas y todo lo que cuelga de ellas,
    # en orden seguro por claves foráneas.
    if not clinica_ids:
        return

    with SesionPruebas() as session:
        # MySQL no permite borrar con una subconsulta sobre la misma
        # tabla, así que primero se obtienen los IDs como listas.
        ubicacion_ids = session.scalars(
            select(Ubicacion.id).where(Ubicacion.clinica_id.in_(clinica_ids))
        ).all()
        equipo_ids = session.scalars(
            select(Equipo.id).where(Equipo.ubicacion_id.in_(ubicacion_ids))
        ).all()
        mantenimiento_ids = session.scalars(
            select(Mantenimiento.id).where(Mantenimiento.equipo_id.in_(equipo_ids))
        ).all()

        # Los mantenimientos van antes que las fallas,
        # porque un mantenimiento puede referenciar una falla.
        session.execute(
            delete(mantenimiento_tecnicos).where(
                mantenimiento_tecnicos.c.mantenimiento_id.in_(mantenimiento_ids)
            )
        )
        session.execute(
            delete(Mantenimiento).where(Mantenimiento.equipo_id.in_(equipo_ids))
        )
        session.execute(delete(Falla).where(Falla.equipo_id.in_(equipo_ids)))
        session.execute(delete(Contrato).where(Contrato.equipo_id.in_(equipo_ids)))
        session.execute(delete(Equipo).where(Equipo.id.in_(equipo_ids)))
        session.execute(delete(Ubicacion).where(Ubicacion.clinica_id.in_(clinica_ids)))
        session.execute(delete(Clinica).where(Clinica.id.in_(clinica_ids)))
        session.commit()


@pytest.fixture
def ubicacion_prueba():
    # Crear una clínica y una ubicación exclusivas para el test.
    with SesionPruebas() as session:
        clinica = Clinica(
            nombre="Clinica temporal para tests",
            direccion="Direccion de prueba",
        )
        session.add(clinica)
        session.flush()

        ubicacion = Ubicacion(
            clinica_id=clinica.id,
            servicio="Servicio de prueba",
            sector="Sector temporal",
        )
        session.add(ubicacion)
        session.commit()

        clinica_id = clinica.id
        ubicacion_id = ubicacion.id

    # Entregar el ID de la ubicación al test.
    yield ubicacion_id

    limpiar_clinicas([clinica_id])


@pytest.fixture
def equipo_prueba(cliente, ubicacion_prueba):
    # Equipo activo en la ubicación temporal; se limpia junto con ella.
    respuesta = cliente.post(
        "/equipos",
        json={
            "nombre": "Equipo de prueba",
            "ubicacion_id": ubicacion_prueba,
            "estado_actual": "activo",
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()


@pytest.fixture
def crear_tecnico_api(cliente):
    # Crea técnicos por la API; al final borra sus asignaciones y a ellos.
    tecnico_ids = []

    def crear(**datos):
        datos.setdefault("nombre", "Tecnico")
        datos.setdefault("apellido", "De Prueba")
        respuesta = cliente.post("/tecnicos", json=datos)
        assert respuesta.status_code == 201
        tecnico_ids.append(respuesta.json()["id"])
        return respuesta.json()

    yield crear

    if tecnico_ids:
        with SesionPruebas() as session:
            session.execute(
                delete(mantenimiento_tecnicos).where(
                    mantenimiento_tecnicos.c.tecnico_id.in_(tecnico_ids)
                )
            )
            session.execute(delete(Tecnico).where(Tecnico.id.in_(tecnico_ids)))
            session.commit()


@pytest.fixture
def crear_clinica_api(cliente):
    # Crea clínicas mediante la API y recuerda sus IDs para limpiarlas,
    # junto con las ubicaciones y equipos que el test les agregue.
    clinica_ids = []

    def crear(**datos):
        datos.setdefault("nombre", "Clinica de prueba")
        respuesta = cliente.post("/clinicas", json=datos)

        if respuesta.status_code == 201:
            clinica_ids.append(respuesta.json()["id"])

        return respuesta

    yield crear

    limpiar_clinicas(clinica_ids)


@pytest.fixture
def crear_ubicacion_api(cliente, crear_clinica_api):
    # Crea una ubicación por la API; sin clinica_id crea también su clínica.
    def crear(clinica_id=None, **datos):
        if clinica_id is None:
            clinica_id = crear_clinica_api().json()["id"]

        datos.setdefault("servicio", "Servicio de prueba")
        respuesta = cliente.post(
            "/ubicaciones",
            json={"clinica_id": clinica_id, **datos},
        )
        assert respuesta.status_code == 201
        return respuesta.json()

    return crear


@pytest.fixture
def base_vacia(cliente):
    # La API y el test comparten una conexión con una transacción abierta:
    # la API ve la base vacía y al final todo se revierte con rollback.
    with engine_pruebas.connect() as conexion:
        transaccion = conexion.begin()
        session = Session(
            bind=conexion,
            join_transaction_mode="create_savepoint",
        )

        def obtener_sesion_compartida():
            yield session

        override_anterior = app.dependency_overrides[obtener_sesion]
        app.dependency_overrides[obtener_sesion] = obtener_sesion_compartida

        try:
            # Vaciar en orden seguro por claves foráneas.
            session.execute(delete(mantenimiento_tecnicos))
            session.execute(delete(Tecnico))
            session.execute(delete(Mantenimiento))
            session.execute(delete(Falla))
            session.execute(delete(Contrato))
            session.execute(delete(Equipo))
            session.execute(delete(Ubicacion))
            session.execute(delete(Clinica))

            # Fijar el vaciado en la transacción externa: así un rollback
            # posterior de la API no lo deshace (solo revierte su savepoint).
            session.commit()
            yield
        finally:
            app.dependency_overrides[obtener_sesion] = override_anterior
            session.close()
            transaccion.rollback()
