import pytest

CAMPOS_TECNICO = {"id", "nombre", "apellido", "empresa"}


@pytest.fixture
def crear_mantenimiento(cliente, equipo_prueba):
    def crear(**datos):
        respuesta = cliente.post("/mantenimientos", json={
            "equipo_id": equipo_prueba["id"],
            "fecha": "2025-04-01",
            "tipo_mantenimiento": "Preventivo",
            **datos,
        })
        assert respuesta.status_code == 201, respuesta.json()
        return respuesta.json()

    return crear


def asignar(cliente, mantenimiento, tecnico):
    respuesta = cliente.post(
        f"/mantenimientos/{mantenimiento['id']}/tecnicos/{tecnico['id']}"
    )
    assert respuesta.status_code == 200
    return respuesta.json()


# --- CRUD de técnicos ---

def test_crear_tecnico_valido_devuelve_formato_esperado(crear_tecnico_api):
    datos = {"nombre": "Ana", "apellido": "Gomez", "empresa": "Siemens"}

    # La fixture ya verifica el 201.
    tecnico = crear_tecnico_api(**datos)

    assert set(tecnico.keys()) == CAMPOS_TECNICO
    assert tecnico == {**datos, "id": tecnico["id"]}


def test_crear_tecnico_sin_empresa(crear_tecnico_api):
    assert crear_tecnico_api()["empresa"] is None


def test_crear_tecnico_con_valores_limite(crear_tecnico_api):
    tecnico = crear_tecnico_api(
        nombre="n" * 100,
        apellido="a" * 100,
        empresa="e" * 100,
    )

    assert tecnico["nombre"] == "n" * 100


@pytest.mark.parametrize(
    "datos",
    [
        {"apellido": "Sin nombre"},
        {"nombre": "Sin apellido"},
        {"nombre": "", "apellido": "Gomez"},
        {"nombre": None, "apellido": "Gomez"},
        {"nombre": "Ana", "apellido": "a" * 101},
        {"nombre": "Ana", "apellido": "Gomez", "empresa": "e" * 101},
    ],
)
def test_crear_tecnico_con_datos_invalidos_devuelve_422(cliente, datos):
    respuesta = cliente.post("/tecnicos", json=datos)

    assert respuesta.status_code == 422


def test_listar_tecnicos_incluye_el_creado(cliente, crear_tecnico_api):
    tecnico = crear_tecnico_api()

    respuesta = cliente.get("/tecnicos")

    assert respuesta.status_code == 200
    assert tecnico in respuesta.json()


def test_listar_tecnicos_sin_registros_devuelve_lista_vacia(
    cliente,
    base_vacia,
):
    respuesta = cliente.get("/tecnicos")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_consultar_tecnico_existente(cliente, crear_tecnico_api):
    tecnico = crear_tecnico_api()

    respuesta = cliente.get(f"/tecnicos/{tecnico['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == tecnico


def test_consultar_tecnico_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/tecnicos/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un técnico con ID 999999."}


@pytest.mark.parametrize(
    "cambios",
    [
        {"nombre": "Bruno"},
        {"apellido": "Perez"},
        {"empresa": "GE HealthCare"},
        {"nombre": "Carla", "apellido": "Diaz", "empresa": "Philips"},
    ],
)
def test_actualizar_tecnico(cliente, crear_tecnico_api, cambios):
    original = crear_tecnico_api(empresa="Siemens")

    respuesta = cliente.put(f"/tecnicos/{original['id']}", json=cambios)

    esperado = {**original, **cambios}
    assert respuesta.status_code == 200
    assert respuesta.json() == esperado
    assert cliente.get(f"/tecnicos/{original['id']}").json() == esperado


def test_actualizar_tecnico_sin_campos_devuelve_400(cliente, crear_tecnico_api):
    original = crear_tecnico_api()

    respuesta = cliente.put(f"/tecnicos/{original['id']}", json={})

    assert respuesta.status_code == 400


def test_actualizar_tecnico_inexistente_devuelve_404(cliente):
    respuesta = cliente.put("/tecnicos/999999", json={"nombre": "No existe"})

    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "cambios",
    [
        {"nombre": None},
        {"apellido": None},
        {"nombre": ""},
        {"apellido": "a" * 101},
        {"empresa": "e" * 101},
    ],
)
def test_actualizar_tecnico_con_datos_invalidos_no_modifica_datos(
    cliente,
    crear_tecnico_api,
    cambios,
):
    original = crear_tecnico_api()

    respuesta = cliente.put(f"/tecnicos/{original['id']}", json=cambios)

    assert respuesta.status_code == 422
    assert cliente.get(f"/tecnicos/{original['id']}").json() == original


def test_eliminar_tecnico_sin_mantenimientos(cliente, crear_tecnico_api):
    tecnico = crear_tecnico_api()

    respuesta = cliente.delete(f"/tecnicos/{tecnico['id']}")

    assert respuesta.status_code == 204
    assert cliente.get(f"/tecnicos/{tecnico['id']}").status_code == 404


def test_eliminar_tecnico_con_mantenimientos_devuelve_409(
    cliente,
    crear_tecnico_api,
    crear_mantenimiento,
):
    tecnico = crear_tecnico_api()
    asignar(cliente, crear_mantenimiento(), tecnico)

    respuesta = cliente.delete(f"/tecnicos/{tecnico['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede eliminar el técnico porque tiene mantenimientos asociados."
        )
    }
    assert cliente.get(f"/tecnicos/{tecnico['id']}").json() == tecnico


def test_eliminar_tecnico_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/tecnicos/999999")

    assert respuesta.status_code == 404


# --- Asignaciones a mantenimientos ---

def test_listar_mantenimientos_de_tecnico(
    cliente,
    crear_tecnico_api,
    crear_mantenimiento,
):
    tecnico = crear_tecnico_api()
    otro = crear_tecnico_api()
    asignado_a = asignar(cliente, crear_mantenimiento(), tecnico)
    asignado_b = asignar(cliente, crear_mantenimiento(fecha="2025-05-01"), tecnico)
    asignar(cliente, crear_mantenimiento(), otro)

    respuesta = cliente.get(f"/tecnicos/{tecnico['id']}/mantenimientos")

    assert respuesta.status_code == 200
    assert {m["id"] for m in respuesta.json()} == {
        asignado_a["id"],
        asignado_b["id"],
    }


def test_listar_mantenimientos_de_tecnico_sin_asignaciones(
    cliente,
    crear_tecnico_api,
):
    tecnico = crear_tecnico_api()

    respuesta = cliente.get(f"/tecnicos/{tecnico['id']}/mantenimientos")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_mantenimientos_de_tecnico_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/tecnicos/999999/mantenimientos")

    assert respuesta.status_code == 404


def test_desasignar_tecnico_de_mantenimiento(
    cliente,
    crear_tecnico_api,
    crear_mantenimiento,
):
    tecnico_a = crear_tecnico_api()
    tecnico_b = crear_tecnico_api()
    mantenimiento = crear_mantenimiento()
    asignar(cliente, mantenimiento, tecnico_a)
    asignar(cliente, mantenimiento, tecnico_b)

    respuesta = cliente.delete(
        f"/mantenimientos/{mantenimiento['id']}/tecnicos/{tecnico_a['id']}"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["tecnico_ids"] == [tecnico_b["id"]]
    assert cliente.get(f"/tecnicos/{tecnico_a['id']}/mantenimientos").json() == []


def test_desasignar_tecnico_no_asignado_es_idempotente(
    cliente,
    crear_tecnico_api,
    crear_mantenimiento,
):
    tecnico = crear_tecnico_api()
    mantenimiento = crear_mantenimiento()

    respuesta = cliente.delete(
        f"/mantenimientos/{mantenimiento['id']}/tecnicos/{tecnico['id']}"
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == mantenimiento


def test_desasignar_tecnico_de_mantenimiento_con_resultado_devuelve_409(
    cliente,
    crear_tecnico_api,
    crear_mantenimiento,
):
    tecnico = crear_tecnico_api()
    mantenimiento = crear_mantenimiento(resultado="Equipo operativo.")
    asignado = asignar(cliente, mantenimiento, tecnico)

    respuesta = cliente.delete(
        f"/mantenimientos/{mantenimiento['id']}/tecnicos/{tecnico['id']}"
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede desasignar un técnico de un mantenimiento "
            "con resultado registrado: forma parte del historial."
        )
    }
    assert cliente.get(
        f"/mantenimientos/{mantenimiento['id']}"
    ).json() == asignado


def test_desasignar_tecnico_inexistente_devuelve_404(
    cliente,
    crear_mantenimiento,
):
    mantenimiento = crear_mantenimiento()

    respuesta = cliente.delete(
        f"/mantenimientos/{mantenimiento['id']}/tecnicos/999999"
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un técnico con ID 999999."}


def test_desasignar_de_mantenimiento_inexistente_devuelve_404(
    cliente,
    crear_tecnico_api,
):
    tecnico = crear_tecnico_api()

    respuesta = cliente.delete(f"/mantenimientos/999999/tecnicos/{tecnico['id']}")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe un mantenimiento con ID 999999."
    }
