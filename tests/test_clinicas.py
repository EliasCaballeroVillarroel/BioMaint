import pytest


# --- Listar ---

def test_listar_clinicas_incluye_clinica_creada(
    cliente,
    crear_clinica_api,
):
    creada = crear_clinica_api(
        nombre="Clinica para listado",
        direccion="Calle 123",
    ).json()

    respuesta = cliente.get("/clinicas")

    assert respuesta.status_code == 200
    assert creada in respuesta.json()


def test_listar_clinicas_sin_registros_devuelve_lista_vacia(
    cliente,
    base_vacia,
):
    respuesta = cliente.get("/clinicas")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


# --- Consultar ---

def test_consultar_clinica_existente(cliente, crear_clinica_api):
    creada = crear_clinica_api(nombre="Clinica para consulta").json()

    respuesta = cliente.get(f"/clinicas/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada


def test_consultar_clinica_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/clinicas/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe una clínica con ID 999999."
    }


# --- Crear ---

def test_crear_clinica_valida_devuelve_formato_esperado(
    crear_clinica_api,
):
    respuesta = crear_clinica_api(
        nombre="Clinica valida",
        direccion="Av. Siempre Viva 742",
    )

    assert respuesta.status_code == 201

    datos = respuesta.json()

    assert set(datos.keys()) == {"id", "nombre", "direccion", "activa"}
    assert isinstance(datos["id"], int)
    assert datos["nombre"] == "Clinica valida"
    assert datos["direccion"] == "Av. Siempre Viva 742"
    assert datos["activa"] is True


def test_crear_clinica_sin_direccion(crear_clinica_api):
    respuesta = crear_clinica_api(nombre="Clinica sin direccion")

    assert respuesta.status_code == 201
    assert respuesta.json()["direccion"] is None


def test_crear_clinica_con_valores_limite(crear_clinica_api):
    respuesta = crear_clinica_api(nombre="n" * 100, direccion="d" * 200)

    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == "n" * 100
    assert respuesta.json()["direccion"] == "d" * 200


@pytest.mark.parametrize(
    "datos",
    [
        {"direccion": "Sin nombre"},
        {"nombre": ""},
        {"nombre": None},
        {"nombre": "n" * 101},
        {"nombre": "Clinica", "direccion": "d" * 201},
    ],
)
def test_crear_clinica_con_datos_invalidos_devuelve_422(cliente, datos):
    respuesta = cliente.post("/clinicas", json=datos)

    assert respuesta.status_code == 422


# --- Actualizar ---

@pytest.mark.parametrize(
    "cambios",
    [
        {"nombre": "Nombre actualizado"},
        {"direccion": "Direccion actualizada"},
        {"nombre": "Ambos", "direccion": "Campos"},
    ],
)
def test_actualizar_clinica(cliente, crear_clinica_api, cambios):
    original = crear_clinica_api(
        nombre="Clinica original",
        direccion="Direccion original",
    ).json()

    respuesta = cliente.put(f"/clinicas/{original['id']}", json=cambios)

    esperado = {**original, **cambios}
    assert respuesta.status_code == 200
    assert respuesta.json() == esperado
    assert cliente.get(f"/clinicas/{original['id']}").json() == esperado


def test_actualizar_clinica_sin_campos_devuelve_400(
    cliente,
    crear_clinica_api,
):
    original = crear_clinica_api(nombre="Clinica original").json()

    respuesta = cliente.put(f"/clinicas/{original['id']}", json={})

    assert respuesta.status_code == 400


def test_actualizar_clinica_inexistente_devuelve_404(cliente):
    respuesta = cliente.put(
        "/clinicas/999999",
        json={"nombre": "No existe"},
    )

    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "cambios",
    [
        {"nombre": ""},
        {"nombre": None},
        {"nombre": "n" * 101},
        {"direccion": "d" * 201},
    ],
)
def test_actualizar_clinica_con_datos_invalidos_no_modifica_datos(
    cliente,
    crear_clinica_api,
    cambios,
):
    original = crear_clinica_api(
        nombre="Clinica original",
        direccion="Direccion original",
    ).json()

    respuesta = cliente.put(f"/clinicas/{original['id']}", json=cambios)

    assert respuesta.status_code == 422
    assert cliente.get(f"/clinicas/{original['id']}").json() == original


# --- Eliminar ---

def test_eliminar_clinica_sin_dependencias(cliente, crear_clinica_api):
    creada = crear_clinica_api(nombre="Clinica a eliminar").json()

    respuesta = cliente.delete(f"/clinicas/{creada['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": (
            f"La clínica con ID {creada['id']} fue eliminada correctamente."
        )
    }
    assert cliente.get(f"/clinicas/{creada['id']}").status_code == 404


def test_eliminar_clinica_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/clinicas/999999")

    assert respuesta.status_code == 404


def test_eliminar_clinica_con_ubicaciones_devuelve_409(
    cliente,
    crear_clinica_api,
    crear_ubicacion_api,
):
    creada = crear_clinica_api(nombre="Clinica con ubicaciones").json()
    crear_ubicacion_api(creada["id"])

    respuesta = cliente.delete(f"/clinicas/{creada['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json()["detail"] == (
        "No se puede eliminar la clínica porque tiene "
        "1 ubicaciones asociadas. "
        f"Para darla de baja usá POST /clinicas/{creada['id']}/baja."
    )

    # La clínica sigue existiendo y activa.
    assert cliente.get(f"/clinicas/{creada['id']}").json() == creada


# --- Baja lógica ---

def test_dar_de_baja_clinica_inactiva_clinica_y_ubicaciones(
    cliente,
    crear_clinica_api,
    crear_ubicacion_api,
):
    creada = crear_clinica_api(nombre="Clinica para baja").json()
    ubicacion_a = crear_ubicacion_api(creada["id"])
    ubicacion_b = crear_ubicacion_api(creada["id"])

    respuesta = cliente.post(f"/clinicas/{creada['id']}/baja")

    assert respuesta.status_code == 200
    assert respuesta.json() == {**creada, "activa": False}

    # El registro se conserva en la base.
    consulta = cliente.get(f"/clinicas/{creada['id']}")
    assert consulta.status_code == 200
    assert consulta.json()["activa"] is False

    for ubicacion in (ubicacion_a, ubicacion_b):
        consulta = cliente.get(f"/ubicaciones/{ubicacion['id']}")
        assert consulta.status_code == 200
        assert consulta.json()["activa"] is False


def test_dar_de_baja_clinica_dos_veces_es_idempotente(
    cliente,
    crear_clinica_api,
):
    creada = crear_clinica_api(nombre="Clinica baja doble").json()

    primera = cliente.post(f"/clinicas/{creada['id']}/baja")
    segunda = cliente.post(f"/clinicas/{creada['id']}/baja")

    assert primera.status_code == 200
    assert segunda.status_code == 200
    assert segunda.json()["activa"] is False


def test_dar_de_baja_clinica_inexistente_devuelve_404(cliente):
    respuesta = cliente.post("/clinicas/999999/baja")

    assert respuesta.status_code == 404


def test_listado_oculta_clinicas_inactivas_salvo_filtro(
    cliente,
    crear_clinica_api,
):
    activa = crear_clinica_api(nombre="Clinica activa").json()
    inactiva = crear_clinica_api(nombre="Clinica inactiva").json()
    cliente.post(f"/clinicas/{inactiva['id']}/baja")

    ids_por_defecto = {c["id"] for c in cliente.get("/clinicas").json()}
    ids_con_filtro = {
        c["id"]
        for c in cliente.get(
            "/clinicas",
            params={"incluir_inactivas": True},
        ).json()
    }

    assert activa["id"] in ids_por_defecto
    assert inactiva["id"] not in ids_por_defecto
    assert {activa["id"], inactiva["id"]} <= ids_con_filtro


def test_actualizar_clinica_dada_de_baja_devuelve_409(
    cliente,
    crear_clinica_api,
):
    creada = crear_clinica_api(nombre="Clinica retirada").json()
    baja = cliente.post(f"/clinicas/{creada['id']}/baja").json()

    respuesta = cliente.put(
        f"/clinicas/{creada['id']}",
        json={"nombre": "No deberia guardarse"},
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"/clinicas/{creada['id']}").json() == baja


def test_crear_ubicacion_en_clinica_dada_de_baja_devuelve_409(
    cliente,
    crear_clinica_api,
):
    creada = crear_clinica_api(nombre="Clinica retirada").json()
    cliente.post(f"/clinicas/{creada['id']}/baja")

    respuesta = cliente.post("/ubicaciones", json={
        "clinica_id": creada["id"],
        "servicio": "No deberia crearse",
    })

    assert respuesta.status_code == 409


def test_mover_ubicacion_a_clinica_dada_de_baja_devuelve_409(
    cliente,
    crear_clinica_api,
    crear_ubicacion_api,
):
    origen = crear_clinica_api(nombre="Clinica origen").json()
    destino = crear_clinica_api(nombre="Clinica destino").json()
    ubicacion = crear_ubicacion_api(origen["id"])
    cliente.post(f"/clinicas/{destino['id']}/baja")

    respuesta = cliente.put(
        f"/ubicaciones/{ubicacion['id']}",
        json={"clinica_id": destino["id"]},
    )

    assert respuesta.status_code == 409
    assert cliente.get(f"/ubicaciones/{ubicacion['id']}").json() == ubicacion


# --- Reactivar ---

def test_reactivar_clinica_reactiva_clinica_y_ubicaciones(
    cliente,
    crear_clinica_api,
    crear_ubicacion_api,
):
    creada = crear_clinica_api(nombre="Clinica para reactivar").json()
    ubicacion = crear_ubicacion_api(creada["id"])
    cliente.post(f"/clinicas/{creada['id']}/baja")

    respuesta = cliente.post(f"/clinicas/{creada['id']}/reactivar")

    assert respuesta.status_code == 200
    assert respuesta.json() == creada

    consulta = cliente.get(f"/ubicaciones/{ubicacion['id']}")
    assert consulta.json()["activa"] is True

    ids = {c["id"] for c in cliente.get("/clinicas").json()}
    assert creada["id"] in ids


def test_reactivar_clinica_inexistente_devuelve_404(cliente):
    respuesta = cliente.post("/clinicas/999999/reactivar")

    assert respuesta.status_code == 404
