from datetime import date, timedelta

import pytest

HOY = date.today()


def dias(n):
    # Fecha relativa a hoy en formato ISO (negativo = pasado).
    return (HOY + timedelta(days=n)).isoformat()


CAMPOS_CONTRATO = {
    "id",
    "equipo_id",
    "tipo_contrato",
    "empresa",
    "fecha_inicio",
    "fecha_fin",
    "estado",
}


@pytest.fixture
def crear_contrato_api(cliente, equipo_prueba):
    # Por defecto, un contrato activo: empezó hace un mes y vence en un año.
    def crear(**datos):
        respuesta = cliente.post(
            "/contratos",
            json={
                "equipo_id": equipo_prueba["id"],
                "tipo_contrato": "Mantenimiento integral",
                "fecha_inicio": dias(-30),
                "fecha_fin": dias(365),
                **datos,
            },
        )
        assert respuesta.status_code == 201, respuesta.json()
        return respuesta.json()

    return crear


# --- Creación y consulta ---


def test_crear_contrato_valido_devuelve_formato_esperado(
    cliente,
    equipo_prueba,
):
    datos = {
        "equipo_id": equipo_prueba["id"],
        "tipo_contrato": "Full risk",
        "empresa": "Siemens",
        "fecha_inicio": dias(-10),
        "fecha_fin": dias(355),
    }

    respuesta = cliente.post("/contratos", json=datos)

    assert respuesta.status_code == 201
    contrato = respuesta.json()
    assert set(contrato.keys()) == CAMPOS_CONTRATO
    assert contrato == {**datos, "id": contrato["id"], "estado": "Activo"}


def test_el_estado_enviado_se_ignora(crear_contrato_api):
    # El estado se calcula con las fechas; no se puede imponer.
    contrato = crear_contrato_api(estado="Vencido")

    assert contrato["estado"] == "Activo"


def test_crear_contrato_con_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.post(
        "/contratos",
        json={
            "equipo_id": 999999,
            "tipo_contrato": "Preventivo",
            "fecha_inicio": dias(-1),
        },
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un equipo con ID 999999."}


def test_crear_contrato_en_equipo_dado_de_baja_devuelve_409(
    cliente,
    equipo_prueba,
):
    cliente.post(f"/equipos/{equipo_prueba['id']}/baja")

    respuesta = cliente.post(
        "/contratos",
        json={
            "equipo_id": equipo_prueba["id"],
            "tipo_contrato": "Preventivo",
            "fecha_inicio": dias(-1),
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": "No se pueden registrar contratos en un equipo dado de baja."
    }


@pytest.mark.parametrize(
    "cambios",
    [
        {"equipo_id": 0},
        {"tipo_contrato": ""},
        {"tipo_contrato": "t" * 101},
        {"empresa": "e" * 101},
        {"fecha_inicio": None},
        {"fecha_fin": dias(-31)},
    ],
)
def test_crear_contrato_con_datos_invalidos_devuelve_422(
    cliente,
    equipo_prueba,
    cambios,
):
    datos = {
        "equipo_id": equipo_prueba["id"],
        "tipo_contrato": "Preventivo",
        "fecha_inicio": dias(-30),
        **cambios,
    }

    respuesta = cliente.post("/contratos", json=datos)

    assert respuesta.status_code == 422
    assert cliente.get(f"/equipos/{equipo_prueba['id']}/contratos").json() == []


def test_listar_contratos_incluye_el_creado(cliente, crear_contrato_api):
    contrato = crear_contrato_api()

    respuesta = cliente.get("/contratos")

    assert respuesta.status_code == 200
    assert contrato in respuesta.json()


def test_listar_contratos_sin_registros_devuelve_lista_vacia(
    cliente,
    base_vacia,
):
    respuesta = cliente.get("/contratos")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_consultar_contrato_existente(cliente, crear_contrato_api):
    contrato = crear_contrato_api()

    respuesta = cliente.get(f"/contratos/{contrato['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == contrato


def test_consultar_contrato_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/contratos/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un contrato con ID 999999."}


# --- Fechas de vigencia ---


@pytest.mark.parametrize(
    ("inicio", "fin", "estado"),
    [
        (-30, 365, "Activo"),
        (-30, None, "Activo"),
        (0, 30, "Activo"),
        (-30, 0, "Activo"),
        (1, 30, "Pendiente"),
        (10, None, "Pendiente"),
        (-60, -1, "Vencido"),
    ],
)
def test_estado_se_calcula_con_las_fechas(
    crear_contrato_api,
    inicio,
    fin,
    estado,
):
    contrato = crear_contrato_api(
        fecha_inicio=dias(inicio),
        fecha_fin=dias(fin) if fin is not None else None,
    )

    assert contrato["estado"] == estado


def test_cambiar_fechas_recalcula_el_estado(cliente, crear_contrato_api):
    contrato = crear_contrato_api()

    respuesta = cliente.put(
        f"/contratos/{contrato['id']}",
        json={"fecha_fin": dias(-1)},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "Vencido"


# --- Equipos y relaciones ---


def test_listar_contratos_de_equipo_ordenados_por_inicio_descendente(
    cliente,
    equipo_prueba,
    ubicacion_prueba,
    crear_contrato_api,
):
    antiguo = crear_contrato_api(fecha_inicio=dias(-800), fecha_fin=dias(-400))
    vigente = crear_contrato_api(fecha_inicio=dias(-399), fecha_fin=dias(300))
    otro_equipo = cliente.post(
        "/equipos",
        json={
            "nombre": "Otro equipo",
            "ubicacion_id": ubicacion_prueba,
            "estado_actual": "activo",
        },
    ).json()
    cliente.post(
        "/contratos",
        json={
            "equipo_id": otro_equipo["id"],
            "tipo_contrato": "Ajeno",
            "fecha_inicio": dias(-5),
        },
    )

    respuesta = cliente.get(f"/equipos/{equipo_prueba['id']}/contratos")

    assert respuesta.status_code == 200
    assert respuesta.json() == [vigente, antiguo]


def test_un_equipo_puede_tener_contratos_superpuestos(crear_contrato_api):
    mantenimiento = crear_contrato_api(tipo_contrato="Mantenimiento")
    calibracion = crear_contrato_api(
        tipo_contrato="Calibracion",
        empresa="Otra empresa",
    )

    assert mantenimiento["estado"] == calibracion["estado"] == "Activo"


def test_listar_contratos_de_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/equipos/999999/contratos")

    assert respuesta.status_code == 404


# --- Actualizar ---


@pytest.mark.parametrize(
    "cambios",
    [
        {"tipo_contrato": "Preventivo"},
        {"empresa": "GE HealthCare"},
        {"fecha_fin": dias(30)},
        {"fecha_fin": None},
    ],
)
def test_actualizar_contrato(cliente, crear_contrato_api, cambios):
    original = crear_contrato_api(empresa="Siemens")

    respuesta = cliente.put(f"/contratos/{original['id']}", json=cambios)

    esperado = {**original, **cambios}
    assert respuesta.status_code == 200
    assert respuesta.json() == esperado
    assert cliente.get(f"/contratos/{original['id']}").json() == esperado


def test_actualizar_contrato_sin_campos_devuelve_400(cliente, crear_contrato_api):
    original = crear_contrato_api()

    respuesta = cliente.put(f"/contratos/{original['id']}", json={})

    assert respuesta.status_code == 400


def test_actualizar_contrato_inexistente_devuelve_404(cliente):
    respuesta = cliente.put("/contratos/999999", json={"empresa": "No existe"})

    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "cambios",
    [
        {"tipo_contrato": None},
        {"tipo_contrato": ""},
        {"fecha_inicio": None},
        # Quedaría el fin antes que el inicio.
        {"fecha_fin": dias(-31)},
    ],
)
def test_actualizar_contrato_con_datos_invalidos_no_modifica_datos(
    cliente,
    crear_contrato_api,
    cambios,
):
    original = crear_contrato_api()

    respuesta = cliente.put(f"/contratos/{original['id']}", json=cambios)

    assert respuesta.status_code == 422
    assert cliente.get(f"/contratos/{original['id']}").json() == original


@pytest.mark.parametrize("nuevo_inicio", [-60, 10])
def test_no_se_puede_mover_el_inicio_de_un_contrato_que_ya_comenzo(
    cliente,
    crear_contrato_api,
    nuevo_inicio,
):
    original = crear_contrato_api(fecha_inicio=dias(-30))

    respuesta = cliente.put(
        f"/contratos/{original['id']}",
        json={"fecha_inicio": dias(nuevo_inicio)},
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede cambiar la fecha de inicio de un contrato que ya comenzó."
        )
    }
    assert cliente.get(f"/contratos/{original['id']}").json() == original

    # Así tampoco se puede volver "pendiente" para poder borrarlo.
    assert cliente.delete(f"/contratos/{original['id']}").status_code == 409


def test_se_puede_mover_el_inicio_de_un_contrato_pendiente(
    cliente,
    crear_contrato_api,
):
    original = crear_contrato_api(fecha_inicio=dias(10), fecha_fin=dias(100))

    respuesta = cliente.put(
        f"/contratos/{original['id']}",
        json={"fecha_inicio": dias(20)},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {**original, "fecha_inicio": dias(20)}


def test_inicio_de_contrato_pendiente_no_puede_quedar_despues_del_fin(
    cliente,
    crear_contrato_api,
):
    original = crear_contrato_api(fecha_inicio=dias(10), fecha_fin=dias(100))

    respuesta = cliente.put(
        f"/contratos/{original['id']}",
        json={"fecha_inicio": dias(101)},
    )

    assert respuesta.status_code == 422
    assert cliente.get(f"/contratos/{original['id']}").json() == original


# --- Cancelar ---


def test_cancelar_contrato(cliente, crear_contrato_api):
    contrato = crear_contrato_api()

    respuesta = cliente.post(f"/contratos/{contrato['id']}/cancelar")

    assert respuesta.status_code == 200
    assert respuesta.json() == {**contrato, "estado": "Cancelado"}
    assert cliente.get(f"/contratos/{contrato['id']}").json()["estado"] == ("Cancelado")


def test_cancelar_contrato_dos_veces_es_idempotente(cliente, crear_contrato_api):
    contrato = crear_contrato_api()

    cliente.post(f"/contratos/{contrato['id']}/cancelar")
    respuesta = cliente.post(f"/contratos/{contrato['id']}/cancelar")

    assert respuesta.status_code == 200
    assert respuesta.json()["estado"] == "Cancelado"


def test_cancelar_contrato_inexistente_devuelve_404(cliente):
    respuesta = cliente.post("/contratos/999999/cancelar")

    assert respuesta.status_code == 404


def test_actualizar_contrato_cancelado_devuelve_409(cliente, crear_contrato_api):
    contrato = crear_contrato_api()
    cancelado = cliente.post(f"/contratos/{contrato['id']}/cancelar").json()

    respuesta = cliente.put(
        f"/contratos/{contrato['id']}",
        json={"empresa": "No deberia guardarse"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": "No se puede modificar un contrato cancelado."
    }
    assert cliente.get(f"/contratos/{contrato['id']}").json() == cancelado


# --- Eliminar e integridad ---


def test_eliminar_contrato_que_no_comenzo(cliente, crear_contrato_api):
    contrato = crear_contrato_api(fecha_inicio=dias(10), fecha_fin=dias(100))

    respuesta = cliente.delete(f"/contratos/{contrato['id']}")

    assert respuesta.status_code == 204
    assert cliente.get(f"/contratos/{contrato['id']}").status_code == 404


@pytest.mark.parametrize("inicio", [0, -30])
def test_eliminar_contrato_que_ya_comenzo_devuelve_409(
    cliente,
    crear_contrato_api,
    inicio,
):
    contrato = crear_contrato_api(fecha_inicio=dias(inicio))

    respuesta = cliente.delete(f"/contratos/{contrato['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede eliminar un contrato que ya comenzó: "
            "forma parte del historial. Se puede cancelar."
        )
    }
    assert cliente.get(f"/contratos/{contrato['id']}").json() == contrato


def test_eliminar_contrato_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/contratos/999999")

    assert respuesta.status_code == 404


def test_no_se_puede_eliminar_un_equipo_con_contratos(
    cliente,
    equipo_prueba,
    crear_contrato_api,
):
    contrato = crear_contrato_api()

    respuesta = cliente.delete(f"/equipos/{equipo_prueba['id']}")

    assert respuesta.status_code == 409
    assert cliente.get(f"/equipos/{equipo_prueba['id']}").status_code == 200
    assert cliente.get(f"/contratos/{contrato['id']}").json() == contrato
