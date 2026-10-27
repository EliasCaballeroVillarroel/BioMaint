from datetime import date, timedelta

import pytest

HOY = date.today()
MANANA = (HOY + timedelta(days=1)).isoformat()

CAMPOS_FALLA = {
    "id",
    "equipo_id",
    "tipo_falla",
    "descripcion_falla",
    "fecha_falla",
    "fecha_resolucion",
    "severidad",
    "resuelta",
}


@pytest.fixture
def crear_falla_api(cliente, equipo_prueba):
    # Crea una falla abierta sobre el equipo de prueba.
    def crear(**datos):
        respuesta = cliente.post(
            "/fallas",
            json={
                "equipo_id": equipo_prueba["id"],
                "tipo_falla": "Electrica",
                "fecha_falla": "2025-03-10",
                **datos,
            },
        )
        assert respuesta.status_code == 201, respuesta.json()
        return respuesta.json()

    return crear


def crear_mantenimiento_api(cliente, falla, fecha):
    respuesta = cliente.post(
        "/mantenimientos",
        json={
            "equipo_id": falla["equipo_id"],
            "falla_id": falla["id"],
            "fecha": fecha,
            "tipo_mantenimiento": "Correctivo",
        },
    )
    assert respuesta.status_code == 201, respuesta.json()
    return respuesta.json()


# --- Crear ---


def test_crear_falla_valida_devuelve_formato_esperado(
    cliente,
    equipo_prueba,
):
    datos = {
        "equipo_id": equipo_prueba["id"],
        "tipo_falla": "Refrigeracion",
        "descripcion_falla": "Temperatura fuera de rango.",
        "fecha_falla": "2025-02-15",
        "severidad": "alta",
    }

    respuesta = cliente.post("/fallas", json=datos)

    assert respuesta.status_code == 201
    falla = respuesta.json()
    assert set(falla.keys()) == CAMPOS_FALLA
    assert falla == {
        **datos,
        "id": falla["id"],
        "fecha_resolucion": None,
        "resuelta": False,
    }


def test_crear_falla_ya_resuelta(crear_falla_api):
    falla = crear_falla_api(
        fecha_falla="2025-02-15",
        fecha_resolucion="2025-02-17",
    )

    assert falla["fecha_resolucion"] == "2025-02-17"
    assert falla["resuelta"] is True


@pytest.mark.parametrize("severidad", ["baja", "media", "alta", "critica"])
def test_crear_falla_acepta_cada_severidad(crear_falla_api, severidad):
    assert crear_falla_api(severidad=severidad)["severidad"] == severidad


def test_crear_falla_con_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.post(
        "/fallas",
        json={
            "equipo_id": 999999,
            "tipo_falla": "Electrica",
            "fecha_falla": "2025-03-10",
        },
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un equipo con ID 999999."}


def test_crear_falla_en_equipo_dado_de_baja_devuelve_409(
    cliente,
    equipo_prueba,
):
    cliente.post(f"/equipos/{equipo_prueba['id']}/baja")

    respuesta = cliente.post(
        "/fallas",
        json={
            "equipo_id": equipo_prueba["id"],
            "tipo_falla": "Electrica",
            "fecha_falla": "2025-03-10",
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": "No se pueden registrar fallas en un equipo dado de baja."
    }
    assert cliente.get(f"/equipos/{equipo_prueba['id']}/fallas").json() == []


@pytest.mark.parametrize(
    "cambios",
    [
        {"equipo_id": 0},
        {"tipo_falla": ""},
        {"tipo_falla": "t" * 101},
        {"tipo_falla": None},
        {"fecha_falla": None},
        {"fecha_falla": MANANA},
        {"fecha_resolucion": MANANA},
        {"fecha_resolucion": "2025-03-09"},
        {"severidad": "ALTA"},
        {"severidad": "urgente"},
    ],
)
def test_crear_falla_con_datos_invalidos_devuelve_422(
    cliente,
    equipo_prueba,
    cambios,
):
    datos = {
        "equipo_id": equipo_prueba["id"],
        "tipo_falla": "Electrica",
        "fecha_falla": "2025-03-10",
        **cambios,
    }

    respuesta = cliente.post("/fallas", json=datos)

    assert respuesta.status_code == 422
    assert cliente.get(f"/equipos/{equipo_prueba['id']}/fallas").json() == []


def test_crear_falla_con_fecha_de_hoy(crear_falla_api):
    falla = crear_falla_api(
        fecha_falla=HOY.isoformat(),
        fecha_resolucion=HOY.isoformat(),
    )

    assert falla["fecha_falla"] == HOY.isoformat()


# --- Listar y consultar ---


def test_listar_fallas_incluye_falla_creada(cliente, crear_falla_api):
    falla = crear_falla_api()

    respuesta = cliente.get("/fallas")

    assert respuesta.status_code == 200
    assert falla in respuesta.json()


def test_listar_fallas_sin_registros_devuelve_lista_vacia(
    cliente,
    base_vacia,
):
    respuesta = cliente.get("/fallas")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_consultar_falla_existente(cliente, crear_falla_api):
    falla = crear_falla_api()

    respuesta = cliente.get(f"/fallas/{falla['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == falla


def test_consultar_falla_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/fallas/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe una falla con ID 999999."}


def test_listar_fallas_de_equipo_ordenadas_por_fecha_descendente(
    cliente,
    equipo_prueba,
    crear_falla_api,
    ubicacion_prueba,
):
    antigua = crear_falla_api(fecha_falla="2024-01-10")
    reciente = crear_falla_api(fecha_falla="2025-06-01")
    otro_equipo = cliente.post(
        "/equipos",
        json={
            "nombre": "Otro equipo",
            "ubicacion_id": ubicacion_prueba,
            "estado_actual": "activo",
        },
    ).json()
    cliente.post(
        "/fallas",
        json={
            "equipo_id": otro_equipo["id"],
            "tipo_falla": "Ajena",
            "fecha_falla": "2025-01-01",
        },
    )

    respuesta = cliente.get(f"/equipos/{equipo_prueba['id']}/fallas")

    assert respuesta.status_code == 200
    assert respuesta.json() == [reciente, antigua]


def test_listar_fallas_de_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/equipos/999999/fallas")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un equipo con ID 999999."}


# --- Actualizar ---


@pytest.mark.parametrize(
    "cambios",
    [
        {"tipo_falla": "Mecanica"},
        {"descripcion_falla": "Descripcion actualizada."},
        {"severidad": "critica"},
        {"fecha_falla": "2025-03-01"},
        {"tipo_falla": "Software", "severidad": "baja"},
    ],
)
def test_actualizar_falla(cliente, crear_falla_api, cambios):
    original = crear_falla_api()

    respuesta = cliente.put(f"/fallas/{original['id']}", json=cambios)

    esperado = {**original, **cambios}
    assert respuesta.status_code == 200
    assert respuesta.json() == esperado
    assert cliente.get(f"/fallas/{original['id']}").json() == esperado


def test_resolver_falla(cliente, crear_falla_api):
    original = crear_falla_api(fecha_falla="2025-03-10")
    assert original["resuelta"] is False

    respuesta = cliente.put(
        f"/fallas/{original['id']}",
        json={"fecha_resolucion": "2025-03-12"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        **original,
        "fecha_resolucion": "2025-03-12",
        "resuelta": True,
    }


def test_resolver_falla_de_equipo_dado_de_baja(
    cliente,
    equipo_prueba,
    crear_falla_api,
):
    # La baja no impide cerrar el historial de las fallas existentes.
    original = crear_falla_api()
    cliente.post(f"/equipos/{equipo_prueba['id']}/baja")

    respuesta = cliente.put(
        f"/fallas/{original['id']}",
        json={"fecha_resolucion": "2025-03-12"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["resuelta"] is True


def test_actualizar_falla_sin_campos_devuelve_400(cliente, crear_falla_api):
    original = crear_falla_api()

    respuesta = cliente.put(f"/fallas/{original['id']}", json={})

    assert respuesta.status_code == 400


def test_actualizar_falla_inexistente_devuelve_404(cliente):
    respuesta = cliente.put(
        "/fallas/999999",
        json={"tipo_falla": "No existe"},
    )

    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "cambios",
    [
        {"tipo_falla": ""},
        {"tipo_falla": None},
        {"fecha_falla": None},
        {"fecha_falla": MANANA},
        {"fecha_resolucion": MANANA},
        {"severidad": "grave"},
        # La resolución quedaría antes que la falla.
        {"fecha_resolucion": "2025-03-01"},
        {"fecha_falla": "2025-03-20", "fecha_resolucion": "2025-03-15"},
    ],
)
def test_actualizar_falla_con_datos_invalidos_no_modifica_datos(
    cliente,
    crear_falla_api,
    cambios,
):
    original = crear_falla_api(fecha_falla="2025-03-10")

    respuesta = cliente.put(f"/fallas/{original['id']}", json=cambios)

    assert respuesta.status_code == 422
    assert cliente.get(f"/fallas/{original['id']}").json() == original


@pytest.mark.parametrize(
    "cambios",
    [
        {"descripcion_falla": "Corrijo la descripcion."},
        {"severidad": "baja"},
        {"fecha_resolucion": "2025-03-13"},
        {"fecha_falla": "2025-03-11"},
    ],
)
def test_una_falla_resuelta_no_se_puede_modificar(
    cliente,
    crear_falla_api,
    cambios,
):
    original = crear_falla_api(
        fecha_falla="2025-03-10",
        fecha_resolucion="2025-03-12",
    )

    respuesta = cliente.put(f"/fallas/{original['id']}", json=cambios)

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede modificar una falla resuelta: si el equipo "
            "volvió a fallar, registrá una falla nueva."
        )
    }
    assert cliente.get(f"/fallas/{original['id']}").json() == original


def test_si_vuelve_a_fallar_se_registra_una_falla_nueva(
    cliente,
    equipo_prueba,
    crear_falla_api,
):
    resuelta = crear_falla_api(
        fecha_falla="2025-03-10",
        fecha_resolucion="2025-03-12",
    )
    nueva = crear_falla_api(fecha_falla="2025-05-02")

    fallas = cliente.get(f"/equipos/{equipo_prueba['id']}/fallas").json()

    assert fallas == [nueva, resuelta]
    assert nueva["resuelta"] is False


def test_fecha_de_falla_no_puede_quedar_despues_de_su_mantenimiento(
    cliente,
    crear_falla_api,
):
    original = crear_falla_api(fecha_falla="2025-03-10")
    crear_mantenimiento_api(cliente, original, "2025-03-11")

    respuesta = cliente.put(
        f"/fallas/{original['id']}",
        json={"fecha_falla": "2025-03-15"},
    )

    assert respuesta.status_code == 422
    assert cliente.get(f"/fallas/{original['id']}").json() == original


# --- Eliminar ---


def test_eliminar_falla_abierta_sin_mantenimientos(cliente, crear_falla_api):
    falla = crear_falla_api()

    respuesta = cliente.delete(f"/fallas/{falla['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": f"La falla con ID {falla['id']} fue eliminada correctamente."
    }
    assert cliente.get(f"/fallas/{falla['id']}").status_code == 404


def test_eliminar_falla_resuelta_devuelve_409(cliente, crear_falla_api):
    falla = crear_falla_api(
        fecha_falla="2025-03-10",
        fecha_resolucion="2025-03-12",
    )

    respuesta = cliente.delete(f"/fallas/{falla['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede eliminar una falla resuelta: forma parte del historial."
        )
    }
    assert cliente.get(f"/fallas/{falla['id']}").json() == falla


def test_eliminar_falla_con_mantenimientos_devuelve_409(
    cliente,
    crear_falla_api,
):
    falla = crear_falla_api()
    crear_mantenimiento_api(cliente, falla, "2025-03-11")

    respuesta = cliente.delete(f"/fallas/{falla['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede eliminar la falla porque tiene mantenimientos asociados."
        )
    }
    assert cliente.get(f"/fallas/{falla['id']}").json() == falla


def test_eliminar_falla_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/fallas/999999")

    assert respuesta.status_code == 404
