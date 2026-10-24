import pytest

CAMPOS_UBICACION = {
    "id",
    "clinica_id",
    "servicio",
    "sector",
    "piso",
    "sala",
    "activa",
}


def crear_equipo_api(cliente, ubicacion_id, numero_serie):
    respuesta = cliente.post("/equipos", json={
        "nombre": "Equipo asociado",
        "ubicacion_id": ubicacion_id,
        "estado_actual": "activo",
        "numero_serie": numero_serie,
    })
    assert respuesta.status_code == 201
    return respuesta.json()


# --- Listar y consultar ---

def test_listar_ubicaciones_incluye_ubicacion_creada(
    cliente,
    crear_ubicacion_api,
):
    creada = crear_ubicacion_api(sector="Sector A", piso="2", sala="201")

    respuesta = cliente.get("/ubicaciones")

    assert respuesta.status_code == 200
    assert creada in respuesta.json()
    assert all(set(u.keys()) == CAMPOS_UBICACION for u in respuesta.json())


def test_listar_ubicaciones_sin_registros_devuelve_lista_vacia(
    cliente,
    base_vacia,
):
    respuesta = cliente.get("/ubicaciones")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listado_oculta_ubicaciones_inactivas_salvo_filtro(
    cliente,
    crear_ubicacion_api,
):
    activa = crear_ubicacion_api()
    inactiva = crear_ubicacion_api()
    cliente.post(f"/clinicas/{inactiva['clinica_id']}/baja")

    ids_por_defecto = {u["id"] for u in cliente.get("/ubicaciones").json()}
    ids_con_filtro = {
        u["id"]
        for u in cliente.get(
            "/ubicaciones",
            params={"incluir_inactivas": True},
        ).json()
    }

    assert activa["id"] in ids_por_defecto
    assert inactiva["id"] not in ids_por_defecto
    assert {activa["id"], inactiva["id"]} <= ids_con_filtro


def test_consultar_ubicacion_existente(cliente, crear_ubicacion_api):
    creada = crear_ubicacion_api()

    respuesta = cliente.get(f"/ubicaciones/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_consultar_ubicacion_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/ubicaciones/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe una ubicación con ID 999999."
    }


# --- Crear ---

def test_crear_ubicacion_valida_devuelve_formato_esperado(
    cliente,
    crear_clinica_api,
):
    clinica = crear_clinica_api().json()
    datos = {
        "clinica_id": clinica["id"],
        "servicio": "Diagnóstico por imágenes",
        "sector": "Tomografía",
        "piso": "PB",
        "sala": "Sala 3",
    }

    respuesta = cliente.post("/ubicaciones", json=datos)

    assert respuesta.status_code == 201
    creada = respuesta.json()
    assert set(creada.keys()) == CAMPOS_UBICACION
    assert isinstance(creada["id"], int)
    assert creada == {**datos, "id": creada["id"], "activa": True}


def test_crear_ubicacion_solo_con_clinica(cliente, crear_clinica_api):
    clinica = crear_clinica_api().json()

    respuesta = cliente.post(
        "/ubicaciones",
        json={"clinica_id": clinica["id"]},
    )

    assert respuesta.status_code == 201
    creada = respuesta.json()
    assert [creada[c] for c in ("servicio", "sector", "piso", "sala")] == [
        None, None, None, None
    ]


def test_crear_ubicacion_con_clinica_inexistente_devuelve_404(cliente):
    respuesta = cliente.post(
        "/ubicaciones",
        json={"clinica_id": 999999, "servicio": "No deberia crearse"},
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe una clínica con ID 999999."
    }


def test_crear_ubicacion_con_valores_limite(crear_ubicacion_api):
    creada = crear_ubicacion_api(
        servicio="s" * 100,
        sector="e" * 100,
        piso="p" * 20,
        sala="a" * 50,
    )

    assert creada["servicio"] == "s" * 100
    assert creada["sector"] == "e" * 100
    assert creada["piso"] == "p" * 20
    assert creada["sala"] == "a" * 50


@pytest.mark.parametrize(
    "datos",
    [
        {"servicio": "s" * 101},
        {"sector": "e" * 101},
        {"piso": "p" * 21},
        {"sala": "a" * 51},
    ],
)
def test_crear_ubicacion_con_texto_demasiado_largo_devuelve_422(
    cliente,
    crear_clinica_api,
    datos,
):
    clinica = crear_clinica_api().json()

    respuesta = cliente.post(
        "/ubicaciones",
        json={"clinica_id": clinica["id"], **datos},
    )

    assert respuesta.status_code == 422


@pytest.mark.parametrize(
    "datos",
    [
        {},
        {"clinica_id": 0},
        {"clinica_id": -1},
        {"clinica_id": None},
    ],
)
def test_crear_ubicacion_con_clinica_invalida_devuelve_422(cliente, datos):
    respuesta = cliente.post(
        "/ubicaciones",
        json={"servicio": "Servicio", **datos},
    )

    assert respuesta.status_code == 422


# --- Actualizar ---

@pytest.mark.parametrize(
    "cambios",
    [
        {"servicio": "Servicio nuevo"},
        {"sector": "Sector nuevo"},
        {"piso": "3"},
        {"sala": "Sala nueva"},
        {"servicio": "Varios", "piso": "1", "sala": "101"},
    ],
)
def test_actualizar_ubicacion(cliente, crear_ubicacion_api, cambios):
    original = crear_ubicacion_api(sector="Original", piso="0", sala="0")

    respuesta = cliente.put(f"/ubicaciones/{original['id']}", json=cambios)

    esperado = {**original, **cambios}
    assert respuesta.status_code == 200
    assert respuesta.json() == esperado
    assert cliente.get(f"/ubicaciones/{original['id']}").json() == esperado


def test_mover_ubicacion_a_otra_clinica_activa(
    cliente,
    crear_clinica_api,
    crear_ubicacion_api,
):
    original = crear_ubicacion_api()
    destino = crear_clinica_api(nombre="Clinica destino").json()

    respuesta = cliente.put(
        f"/ubicaciones/{original['id']}",
        json={"clinica_id": destino["id"]},
    )

    assert respuesta.status_code == 200
    assert respuesta.json() == {**original, "clinica_id": destino["id"]}


def test_actualizar_ubicacion_sin_campos_devuelve_400(
    cliente,
    crear_ubicacion_api,
):
    original = crear_ubicacion_api()

    respuesta = cliente.put(f"/ubicaciones/{original['id']}", json={})

    assert respuesta.status_code == 400
    assert respuesta.json() == {
        "detail": "Debés enviar al menos un campo para actualizar."
    }


def test_actualizar_ubicacion_inexistente_devuelve_404(cliente):
    respuesta = cliente.put(
        "/ubicaciones/999999",
        json={"servicio": "No existe"},
    )

    assert respuesta.status_code == 404


def test_mover_ubicacion_a_clinica_inexistente_no_modifica_datos(
    cliente,
    crear_ubicacion_api,
):
    original = crear_ubicacion_api()

    respuesta = cliente.put(
        f"/ubicaciones/{original['id']}",
        json={"clinica_id": 999999, "servicio": "No deberia guardarse"},
    )

    assert respuesta.status_code == 404
    assert cliente.get(f"/ubicaciones/{original['id']}").json() == original


@pytest.mark.parametrize(
    "cambios",
    [
        {"clinica_id": 0},
        {"clinica_id": None},
        {"servicio": "s" * 101},
        {"piso": "p" * 21},
        {"sala": "a" * 51},
    ],
)
def test_actualizar_ubicacion_con_datos_invalidos_no_modifica_datos(
    cliente,
    crear_ubicacion_api,
    cambios,
):
    original = crear_ubicacion_api()

    respuesta = cliente.put(f"/ubicaciones/{original['id']}", json=cambios)

    assert respuesta.status_code == 422
    assert cliente.get(f"/ubicaciones/{original['id']}").json() == original


def test_actualizar_ubicacion_dada_de_baja_devuelve_409(
    cliente,
    crear_ubicacion_api,
):
    ubicacion = crear_ubicacion_api()
    cliente.post(f"/clinicas/{ubicacion['clinica_id']}/baja")
    inactiva = cliente.get(f"/ubicaciones/{ubicacion['id']}").json()

    respuesta = cliente.put(
        f"/ubicaciones/{ubicacion['id']}",
        json={"servicio": "No deberia guardarse"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": "No se puede modificar una ubicación dada de baja."
    }
    assert cliente.get(f"/ubicaciones/{ubicacion['id']}").json() == inactiva


def test_mover_ubicacion_dada_de_baja_a_clinica_activa_devuelve_409(
    cliente,
    crear_clinica_api,
    crear_ubicacion_api,
):
    ubicacion = crear_ubicacion_api()
    destino = crear_clinica_api(nombre="Clinica activa").json()
    cliente.post(f"/clinicas/{ubicacion['clinica_id']}/baja")
    inactiva = cliente.get(f"/ubicaciones/{ubicacion['id']}").json()

    respuesta = cliente.put(
        f"/ubicaciones/{ubicacion['id']}",
        json={"clinica_id": destino["id"]},
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"/ubicaciones/{ubicacion['id']}").json() == inactiva


# --- Eliminar ---

def test_eliminar_ubicacion_sin_equipos(cliente, crear_ubicacion_api):
    ubicacion = crear_ubicacion_api()

    respuesta = cliente.delete(f"/ubicaciones/{ubicacion['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": (
            f"La ubicación con ID {ubicacion['id']} "
            "fue eliminada correctamente."
        )
    }
    assert cliente.get(f"/ubicaciones/{ubicacion['id']}").status_code == 404


def test_eliminar_ubicacion_con_equipos_devuelve_409(
    cliente,
    crear_ubicacion_api,
):
    ubicacion = crear_ubicacion_api()
    crear_equipo_api(cliente, ubicacion["id"], "TEST-UBIC-DEL-001")

    respuesta = cliente.delete(f"/ubicaciones/{ubicacion['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede eliminar la ubicación porque tiene equipos asociados."
        )
    }
    assert cliente.get(f"/ubicaciones/{ubicacion['id']}").json() == ubicacion


def test_eliminar_ubicacion_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/ubicaciones/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe una ubicación con ID 999999."
    }


# --- Relación con equipos ---

def test_listar_equipos_de_ubicacion(cliente, crear_ubicacion_api):
    ubicacion = crear_ubicacion_api()
    otra = crear_ubicacion_api()
    equipo_a = crear_equipo_api(cliente, ubicacion["id"], "TEST-UBIC-EQ-A")
    equipo_b = crear_equipo_api(cliente, ubicacion["id"], "TEST-UBIC-EQ-B")
    crear_equipo_api(cliente, otra["id"], "TEST-UBIC-EQ-OTRA")

    respuesta = cliente.get(f"/ubicaciones/{ubicacion['id']}/equipos")

    assert respuesta.status_code == 200
    assert sorted(respuesta.json(), key=lambda e: e["id"]) == [
        equipo_a,
        equipo_b,
    ]


def test_listar_equipos_de_ubicacion_sin_equipos(
    cliente,
    crear_ubicacion_api,
):
    ubicacion = crear_ubicacion_api()

    respuesta = cliente.get(f"/ubicaciones/{ubicacion['id']}/equipos")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_listar_equipos_de_ubicacion_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/ubicaciones/999999/equipos")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe una ubicación con ID 999999."
    }
