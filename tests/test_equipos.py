import pytest


def test_crear_y_consultar_equipo(cliente, ubicacion_prueba):
    datos = {
        "nombre": "Ecografo de prueba",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "tipo": "Ecografia",
        "modelo": "Modelo TEST",
        "marca": "Marca TEST",
        "numero_serie": "TEST-BIOM-001",
    }

    # Creamos el equipo mediante la API.
    respuesta_creacion = cliente.post("/equipos", json=datos)

    assert respuesta_creacion.status_code == 201

    equipo_creado = respuesta_creacion.json()

    assert equipo_creado["nombre"] == datos["nombre"]
    assert equipo_creado["ubicacion_id"] == ubicacion_prueba
    assert equipo_creado["numero_serie"] == datos["numero_serie"]

    # Consultamos el equipo usando el ID que devolvió la API.
    equipo_id = equipo_creado["id"]
    respuesta_consulta = cliente.get(f"/equipos/{equipo_id}")

    assert respuesta_consulta.status_code == 200
    assert respuesta_consulta.json()["id"] == equipo_id
    assert respuesta_consulta.json()["nombre"] == datos["nombre"]


def test_consultar_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/equipos/999999")

    assert respuesta.status_code == 404

def test_crear_equipo_con_ubicacion_inexistente_devuelve_404(cliente):
    datos = {
        "nombre": "Equipo de prueba",
        "ubicacion_id": 999999,
        "estado_actual": "activo",
        "tipo": "Ecografia",
    }

    respuesta = cliente.post("/equipos", json=datos)

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe una ubicación con ID 999999."
    }


def test_crear_equipo_con_estado_invalido_devuelve_422(
    cliente,
    ubicacion_prueba,
):
    datos = {
        "nombre": "Equipo de prueba",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "ESTADO_QUE_NO_EXISTE",
        "tipo": "Ecografia",
    }

    respuesta = cliente.post("/equipos", json=datos)

    assert respuesta.status_code == 422


def test_crear_equipo_con_numero_serie_duplicado_devuelve_409(
    cliente,
    ubicacion_prueba,
):
    datos = {
        "nombre": "Ecografo original",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "tipo": "Ecografia",
        "numero_serie": "TEST-SERIE-DUPLICADA-001",
    }

    # Primera solicitud: debe crear el equipo.
    primera_respuesta = cliente.post("/equipos", json=datos)

    assert primera_respuesta.status_code == 201

    # Segunda solicitud: reutilizamos exactamente el mismo número de serie.
    segundo_equipo = datos.copy()
    segundo_equipo["nombre"] = "Ecografo duplicado"

    segunda_respuesta = cliente.post("/equipos", json=segundo_equipo)

    assert segunda_respuesta.status_code == 409


def test_actualizar_equipo_existente(cliente, ubicacion_prueba):
    # Creamos primero un equipo para tener uno que actualizar.
    datos = {
        "nombre": "Ecografo original",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "tipo": "Ecografia",
        "numero_serie": "TEST-ACTUALIZAR-001",
    }

    respuesta_creacion = cliente.post("/equipos", json=datos)
    assert respuesta_creacion.status_code == 201

    equipo_id = respuesta_creacion.json()["id"]

    # Actualizamos solamente el nombre.
    respuesta_actualizacion = cliente.put(
        f"/equipos/{equipo_id}",
        json={"nombre": "Ecografo actualizado"},
    )

    assert respuesta_actualizacion.status_code == 200
    assert respuesta_actualizacion.json()["nombre"] == "Ecografo actualizado"
    assert respuesta_actualizacion.json()["id"] == equipo_id


def test_actualizar_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.put(
        "/equipos/999999",
        json={"nombre": "Nombre actualizado"},
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe un equipo con ID 999999."
    }
def test_actualizar_equipo_con_ubicacion_inexistente_devuelve_404(
    cliente,
    ubicacion_prueba,
):
    datos = {
        "nombre": "Ecografo para actualizar",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "tipo": "Ecografia",
        "numero_serie": "TEST-UBICACION-001",
    }

    respuesta_creacion = cliente.post("/equipos", json=datos)
    assert respuesta_creacion.status_code == 201

    equipo_id = respuesta_creacion.json()["id"]

    respuesta_actualizacion = cliente.put(
        f"/equipos/{equipo_id}",
        json={"ubicacion_id": 999999},
    )

    assert respuesta_actualizacion.status_code == 404
    assert respuesta_actualizacion.json() == {
        "detail": "No existe una ubicación con ID 999999."
    }

    # Comprobamos que el equipo conserve su ubicación original.
    respuesta_consulta = cliente.get(f"/equipos/{equipo_id}")

    assert respuesta_consulta.status_code == 200
    assert respuesta_consulta.json()["ubicacion_id"] == ubicacion_prueba


def test_actualizar_equipo_sin_campos_devuelve_400(
    cliente,
    ubicacion_prueba,
):
    datos = {
        "nombre": "Ecografo sin cambios",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "tipo": "Ecografia",
        "numero_serie": "TEST-SIN-CAMBIOS-001",
    }

    respuesta_creacion = cliente.post("/equipos", json=datos)
    assert respuesta_creacion.status_code == 201

    equipo_id = respuesta_creacion.json()["id"]

    respuesta_actualizacion = cliente.put(
        f"/equipos/{equipo_id}",
        json={},
    )

    assert respuesta_actualizacion.status_code == 400
    assert respuesta_actualizacion.json() == {
        "detail": "Debés enviar al menos un campo para actualizar."
    }


def test_eliminar_equipo_existente(cliente, ubicacion_prueba):
    # Creamos un equipo para la prueba.
    datos_equipo = {
        "nombre": "Equipo para probar eliminación",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-DELETE-001"
    }

    respuesta_creacion = cliente.post("/equipos", json=datos_equipo)

    assert respuesta_creacion.status_code == 201

    equipo_id = respuesta_creacion.json()["id"]

    # Eliminamos el equipo recién creado.
    respuesta_eliminacion = cliente.delete(f"/equipos/{equipo_id}")

    assert respuesta_eliminacion.status_code in (200, 204)

    # Verificamos que ya no se pueda consultar.
    respuesta_consulta = cliente.get(f"/equipos/{equipo_id}")

    assert respuesta_consulta.status_code == 404


def test_eliminar_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/equipos/999999")

    assert respuesta.status_code == 404


def test_dar_de_baja_equipo_conserva_el_registro(
    cliente,
    ubicacion_prueba,
):
    datos = {
        "nombre": "Ecografo para dar de baja",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-BAJA-001",
    }

    respuesta_creacion = cliente.post("/equipos", json=datos)
    assert respuesta_creacion.status_code == 201

    equipo_id = respuesta_creacion.json()["id"]

    respuesta_baja = cliente.post(f"/equipos/{equipo_id}/baja")

    assert respuesta_baja.status_code == 200
    assert respuesta_baja.json()["estado_actual"] == "dado_de_baja"

    # El equipo debe seguir existiendo.
    respuesta_consulta = cliente.get(f"/equipos/{equipo_id}")

    assert respuesta_consulta.status_code == 200
    assert respuesta_consulta.json()["id"] == equipo_id
    assert respuesta_consulta.json()["estado_actual"] == "dado_de_baja"


def test_dar_de_baja_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.post("/equipos/999999/baja")

    assert respuesta.status_code == 404

def test_no_se_puede_actualizar_equipo_dado_de_baja(
    cliente,
    ubicacion_prueba,
):
    datos = {
        "nombre": "Equipo retirado",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-BAJA-002",
    }

    creado = cliente.post("/equipos", json=datos)
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]

    baja = cliente.post(f"/equipos/{equipo_id}/baja")
    assert baja.status_code == 200

    actualizacion = cliente.put(
        f"/equipos/{equipo_id}",
        json={"estado_actual": "activo"},
    )

    assert actualizacion.status_code == 409
    assert actualizacion.json()["detail"] == (
        "No se puede modificar un equipo que está dado de baja."
    )

    consulta = cliente.get(f"/equipos/{equipo_id}")
    assert consulta.status_code == 200
    assert consulta.json()["estado_actual"] == "dado_de_baja"


def test_listar_equipos_incluye_equipo_creado(
    cliente,
    ubicacion_prueba,
):
    datos = {
        "nombre": "Equipo para probar listado",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-LISTADO-001",
    }

    creacion = cliente.post("/equipos", json=datos)
    assert creacion.status_code == 201

    equipo_id = creacion.json()["id"]

    respuesta = cliente.get("/equipos")

    assert respuesta.status_code == 200
    assert isinstance(respuesta.json(), list)

    equipos = respuesta.json()
    equipo_encontrado = next(
        (equipo for equipo in equipos if equipo["id"] == equipo_id),
        None,
    )

    assert equipo_encontrado is not None
    assert equipo_encontrado["nombre"] == datos["nombre"]
    assert equipo_encontrado["ubicacion_id"] == ubicacion_prueba
    assert equipo_encontrado["estado_actual"] == "activo"
    assert equipo_encontrado["numero_serie"] == datos["numero_serie"]


def test_listar_equipos_sin_registros_devuelve_lista_vacia(
    cliente,
    base_vacia,
):
    respuesta = cliente.get("/equipos")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_actualizar_nombre_equipo(cliente, ubicacion_prueba):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo original",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-UPD-NOMBRE-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]
    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"nombre": "Ecografo actualizado"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Ecografo actualizado"


def test_actualizar_estado_equipo(cliente, ubicacion_prueba):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo para estado",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-UPD-ESTADO-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]
    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"estado_actual": "mantenimiento"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["estado_actual"] == "mantenimiento"


def test_actualizar_tipo_equipo(cliente, ubicacion_prueba):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo para tipo",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-UPD-TIPO-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]
    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"tipo": "Ecografo"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["tipo"] == "Ecografo"


def test_actualizar_modelo_equipo(cliente, ubicacion_prueba):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo para modelo",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-UPD-MODELO-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]
    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"modelo": "Modelo X2"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["modelo"] == "Modelo X2"


def test_actualizar_marca_equipo(cliente, ubicacion_prueba):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo para marca",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-UPD-MARCA-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]
    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"marca": "Marca de prueba"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["marca"] == "Marca de prueba"


def test_actualizar_numero_serie_equipo(cliente, ubicacion_prueba):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo para serie",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-UPD-SERIE-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]
    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"numero_serie": "TEST-ACTUALIZADO-001"},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["numero_serie"] == "TEST-ACTUALIZADO-001"


def test_actualizar_ubicacion_equipo(
    cliente,
    ubicacion_prueba,
    crear_ubicacion_api,
):
    nueva_ubicacion_id = crear_ubicacion_api()["id"]
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-UPD-UBICACION-001"
    )

    respuesta = cliente.put(
        f"/equipos/{original['id']}",
        json={"ubicacion_id": nueva_ubicacion_id},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["ubicacion_id"] == nueva_ubicacion_id

    consulta = cliente.get(f"/equipos/{original['id']}")
    assert consulta.status_code == 200
    assert consulta.json()["ubicacion_id"] == nueva_ubicacion_id


def test_crear_equipo_con_nombre_vacio_devuelve_422(
    cliente,
    ubicacion_prueba,
):
    respuesta = cliente.post("/equipos", json={
        "nombre": "",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
    })

    assert respuesta.status_code == 422


def test_crear_equipo_con_ubicacion_cero_devuelve_422(cliente):
    respuesta = cliente.post("/equipos", json={
        "nombre": "Equipo de prueba",
        "ubicacion_id": 0,
        "estado_actual": "activo",
    })

    assert respuesta.status_code == 422


def test_crear_equipo_con_numero_serie_vacio_devuelve_422(
    cliente,
    ubicacion_prueba,
):
    respuesta = cliente.post("/equipos", json={
        "nombre": "Equipo de prueba",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "",
    })

    assert respuesta.status_code == 422


def test_crear_equipo_sin_estado_devuelve_422(
    cliente,
    ubicacion_prueba,
):
    respuesta = cliente.post("/equipos", json={
        "nombre": "Equipo de prueba",
        "ubicacion_id": ubicacion_prueba,
    })

    assert respuesta.status_code == 422


def test_actualizar_equipo_con_nombre_vacio_devuelve_422(
    cliente,
    ubicacion_prueba,
):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo original",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-LIMITE-NOMBRE-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]

    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"nombre": ""},
    )

    assert respuesta.status_code == 422

    consulta = cliente.get(f"/equipos/{equipo_id}")
    assert consulta.status_code == 200
    assert consulta.json()["nombre"] == "Equipo original"


def test_actualizar_equipo_con_numero_serie_vacio_devuelve_422(
    cliente,
    ubicacion_prueba,
):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo original",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-LIMITE-SERIE-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]

    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"numero_serie": ""},
    )

    assert respuesta.status_code == 422

    consulta = cliente.get(f"/equipos/{equipo_id}")
    assert consulta.status_code == 200
    assert consulta.json()["numero_serie"] == "TEST-LIMITE-SERIE-001"


def test_actualizar_numero_serie_duplicado_no_modifica_equipos(
    cliente,
    ubicacion_prueba,
):
    equipo_a = cliente.post("/equipos", json={
        "nombre": "Equipo A",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-DUPLICADO-A",
    })
    assert equipo_a.status_code == 201

    equipo_b = cliente.post("/equipos", json={
        "nombre": "Equipo B",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-DUPLICADO-B",
    })
    assert equipo_b.status_code == 201

    id_a = equipo_a.json()["id"]
    id_b = equipo_b.json()["id"]

    respuesta = cliente.put(
        f"/equipos/{id_b}",
        json={"numero_serie": "TEST-DUPLICADO-A"},
    )

    assert respuesta.status_code == 409

    consulta_a = cliente.get(f"/equipos/{id_a}")
    consulta_b = cliente.get(f"/equipos/{id_b}")

    assert consulta_a.status_code == 200
    assert consulta_b.status_code == 200

    assert consulta_a.json()["numero_serie"] == "TEST-DUPLICADO-A"
    assert consulta_b.json()["numero_serie"] == "TEST-DUPLICADO-B"


def test_reactivar_equipo_dado_de_baja_no_modifica_estado(
    cliente,
    ubicacion_prueba,
):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo retirado",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-REACTIVACION-001",
    })
    assert creado.status_code == 201

    equipo_id = creado.json()["id"]

    baja = cliente.post(f"/equipos/{equipo_id}/baja")
    assert baja.status_code == 200

    respuesta = cliente.put(
        f"/equipos/{equipo_id}",
        json={"estado_actual": "activo"},
    )

    assert respuesta.status_code == 409

    consulta = cliente.get(f"/equipos/{equipo_id}")
    assert consulta.status_code == 200
    assert consulta.json()["estado_actual"] == "dado_de_baja"


def test_crear_equipo_devuelve_formato_esperado(
    cliente,
    ubicacion_prueba,
):
    respuesta = cliente.post("/equipos", json={
        "nombre": "Equipo para validar respuesta",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "tipo": "Ecografo",
        "modelo": "Modelo QA",
        "marca": "Marca QA",
        "numero_serie": "TEST-FORMATO-001",
    })

    assert respuesta.status_code == 201

    datos = respuesta.json()

    campos_obligatorios = {
        "id",
        "nombre",
        "ubicacion_id",
        "estado_actual",
        "tipo",
        "modelo",
        "marca",
        "numero_serie",
        "ubicacion_activa",
    }

    assert set(datos.keys()) == campos_obligatorios
    assert datos["ubicacion_activa"] is True
    assert isinstance(datos["id"], int)
    assert isinstance(datos["nombre"], str)
    assert isinstance(datos["ubicacion_id"], int)
    assert isinstance(datos["estado_actual"], str)
    assert datos["nombre"] == "Equipo para validar respuesta"
    assert datos["estado_actual"] == "activo"


def test_error_equipo_inexistente_tiene_formato_esperado(cliente):
    respuesta = cliente.get("/equipos/999999")

    assert respuesta.status_code == 404
    assert respuesta.headers["content-type"].startswith(
        "application/json"
    )

    datos = respuesta.json()

    assert set(datos.keys()) == {"detail"}
    assert datos["detail"] == "No existe un equipo con ID 999999."


def test_listado_devuelve_elementos_con_formato_equipo(
    cliente,
    ubicacion_prueba,
):
    creado = cliente.post("/equipos", json={
        "nombre": "Equipo de listado QA",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": "TEST-FORMATO-LISTA-001",
    })
    assert creado.status_code == 201

    respuesta = cliente.get("/equipos")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith(
        "application/json"
    )

    equipos = respuesta.json()
    assert isinstance(equipos, list)

    equipo = next(
        (
            elemento
            for elemento in equipos
            if elemento["id"] == creado.json()["id"]
        ),
        None,
    )

    assert equipo is not None
    assert set(equipo.keys()) == {
        "id",
        "nombre",
        "ubicacion_id",
        "estado_actual",
        "tipo",
        "modelo",
        "marca",
        "numero_serie",
        "ubicacion_activa",
    }


# --- Valores límite, nulos y actualizaciones fallidas ---

def crear_equipo_prueba(cliente, ubicacion_id, numero_serie, **extra):
    datos = {
        "nombre": "Equipo original",
        "ubicacion_id": ubicacion_id,
        "estado_actual": "activo",
        "tipo": "Tipo original",
        "modelo": "Modelo original",
        "marca": "Marca original",
        "numero_serie": numero_serie,
    }
    datos.update(extra)

    respuesta = cliente.post("/equipos", json=datos)
    assert respuesta.status_code == 201
    return respuesta.json()


def test_crear_equipo_con_campos_de_100_caracteres(
    cliente,
    ubicacion_prueba,
):
    texto_limite = "x" * 100

    respuesta = cliente.post("/equipos", json={
        "nombre": texto_limite,
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "tipo": texto_limite,
        "modelo": texto_limite,
        "marca": texto_limite,
        "numero_serie": "S" * 100,
    })

    assert respuesta.status_code == 201
    assert respuesta.json()["nombre"] == texto_limite
    assert respuesta.json()["numero_serie"] == "S" * 100


@pytest.mark.parametrize(
    "campo",
    ["nombre", "tipo", "modelo", "marca", "numero_serie"],
)
def test_crear_equipo_con_campo_de_101_caracteres_devuelve_422(
    cliente,
    ubicacion_prueba,
    campo,
):
    datos = {
        "nombre": "Equipo de prueba",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "activo",
        "numero_serie": f"TEST-LARGO-{campo}",
    }
    datos[campo] = "x" * 101

    respuesta = cliente.post("/equipos", json=datos)

    assert respuesta.status_code == 422


def test_crear_equipo_con_ubicacion_negativa_devuelve_422(cliente):
    respuesta = cliente.post("/equipos", json={
        "nombre": "Equipo de prueba",
        "ubicacion_id": -1,
        "estado_actual": "activo",
    })

    assert respuesta.status_code == 422


@pytest.mark.parametrize(
    "cambios",
    [
        {"nombre": "x" * 101},
        {"marca": "x" * 101},
        {"numero_serie": "x" * 101},
        {"estado_actual": "estado_inexistente"},
        {"ubicacion_id": 0},
        {"ubicacion_id": -5},
    ],
)
def test_actualizar_equipo_con_valor_fuera_de_limite_devuelve_422(
    cliente,
    ubicacion_prueba,
    cambios,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-LIMITE-UPD-001"
    )

    respuesta = cliente.put(f"/equipos/{original['id']}", json=cambios)

    assert respuesta.status_code == 422

    consulta = cliente.get(f"/equipos/{original['id']}")
    assert consulta.json() == original


@pytest.mark.parametrize(
    "campo",
    ["nombre", "estado_actual", "ubicacion_id"],
)
def test_actualizar_campo_obligatorio_a_null_devuelve_422(
    cliente,
    ubicacion_prueba,
    campo,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-NULL-OBLIG-001"
    )

    respuesta = cliente.put(
        f"/equipos/{original['id']}",
        json={campo: None},
    )

    assert respuesta.status_code == 422

    consulta = cliente.get(f"/equipos/{original['id']}")
    assert consulta.json() == original


def test_actualizar_varios_campos_a_la_vez(cliente, ubicacion_prueba):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-UPD-VARIOS-001"
    )

    cambios = {
        "nombre": "Nombre nuevo",
        "estado_actual": "inactivo",
        "marca": "Marca nueva",
    }

    respuesta = cliente.put(f"/equipos/{original['id']}", json=cambios)

    assert respuesta.status_code == 200

    esperado = {**original, **cambios}
    assert respuesta.json() == esperado
    assert cliente.get(f"/equipos/{original['id']}").json() == esperado


def test_actualizar_con_ubicacion_inexistente_no_modifica_otros_campos(
    cliente,
    ubicacion_prueba,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-UBIC-FALLIDA-001"
    )

    respuesta = cliente.put(
        f"/equipos/{original['id']}",
        json={"nombre": "No deberia guardarse", "ubicacion_id": 999999},
    )

    assert respuesta.status_code == 404

    consulta = cliente.get(f"/equipos/{original['id']}")
    assert consulta.json() == original


def test_actualizar_equipo_dado_de_baja_no_modifica_ningun_campo(
    cliente,
    ubicacion_prueba,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-BAJA-VARIOS-001"
    )

    baja = cliente.post(f"/equipos/{original['id']}/baja")
    assert baja.status_code == 200
    dado_de_baja = baja.json()

    respuesta = cliente.put(
        f"/equipos/{original['id']}",
        json={
            "nombre": "No deberia guardarse",
            "marca": "Tampoco",
            "numero_serie": "TEST-BAJA-VARIOS-002",
        },
    )

    assert respuesta.status_code == 409

    consulta = cliente.get(f"/equipos/{original['id']}")
    assert consulta.json() == dado_de_baja


def test_eliminar_equipo_devuelve_formato_esperado(
    cliente,
    ubicacion_prueba,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-FORMATO-DELETE-001"
    )

    respuesta = cliente.delete(f"/equipos/{original['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        "mensaje": (
            f"El equipo con ID {original['id']} "
            "fue eliminado correctamente."
        )
    }


def test_dar_de_baja_devuelve_formato_esperado(
    cliente,
    ubicacion_prueba,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-FORMATO-BAJA-001"
    )

    respuesta = cliente.post(f"/equipos/{original['id']}/baja")

    assert respuesta.status_code == 200
    assert respuesta.json() == {
        **original,
        "estado_actual": "dado_de_baja",
    }


# --- Ubicaciones dadas de baja ---

@pytest.fixture
def ubicacion_dada_de_baja(cliente, crear_ubicacion_api):
    ubicacion = crear_ubicacion_api()
    baja = cliente.post(f"/clinicas/{ubicacion['clinica_id']}/baja")
    assert baja.status_code == 200
    return ubicacion["id"]


def test_crear_equipo_en_ubicacion_dada_de_baja_devuelve_409(
    cliente,
    ubicacion_dada_de_baja,
):
    ubicacion_id = ubicacion_dada_de_baja

    respuesta = cliente.post("/equipos", json={
        "nombre": "No deberia crearse",
        "ubicacion_id": ubicacion_id,
        "estado_actual": "activo",
        "numero_serie": "TEST-UBIC-INACTIVA-001",
    })

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": "No se pueden crear equipos en una ubicación dada de baja."
    }

    equipos = cliente.get(f"/ubicaciones/{ubicacion_id}/equipos").json()
    assert equipos == []


def test_mover_equipo_a_ubicacion_dada_de_baja_devuelve_409(
    cliente,
    ubicacion_prueba,
    ubicacion_dada_de_baja,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-MOVER-INACTIVA-001"
    )
    ubicacion_id = ubicacion_dada_de_baja

    respuesta = cliente.put(
        f"/equipos/{original['id']}",
        json={"ubicacion_id": ubicacion_id, "nombre": "No deberia guardarse"},
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": "No se puede mover un equipo a una ubicación dada de baja."
    }
    assert cliente.get(f"/equipos/{original['id']}").json() == original


def test_equipo_de_clinica_dada_de_baja_queda_marcado_y_sigue_operativo(
    cliente,
    ubicacion_prueba,
    crear_ubicacion_api,
):
    ubicacion = crear_ubicacion_api()
    original = crear_equipo_prueba(
        cliente, ubicacion["id"], "TEST-MARCA-BAJA-001"
    )
    assert original["ubicacion_activa"] is True

    cliente.post(f"/clinicas/{ubicacion['clinica_id']}/baja")

    # Queda marcado, pero conserva su estado.
    consulta = cliente.get(f"/equipos/{original['id']}").json()
    assert consulta == {**original, "ubicacion_activa": False}

    # Se puede seguir actualizando sin moverlo.
    respuesta = cliente.put(
        f"/equipos/{original['id']}",
        json={"nombre": "Sigue operativo", "ubicacion_id": ubicacion["id"]},
    )
    assert respuesta.status_code == 200
    assert respuesta.json()["nombre"] == "Sigue operativo"

    # Y se puede trasladar a una ubicación activa.
    traslado = cliente.put(
        f"/equipos/{original['id']}",
        json={"ubicacion_id": ubicacion_prueba},
    )
    assert traslado.status_code == 200
    assert traslado.json()["ubicacion_activa"] is True


def test_crear_equipo_dado_de_baja_devuelve_422(cliente, ubicacion_prueba):
    respuesta = cliente.post("/equipos", json={
        "nombre": "Equipo de prueba",
        "ubicacion_id": ubicacion_prueba,
        "estado_actual": "dado_de_baja",
    })

    assert respuesta.status_code == 422


def test_actualizar_estado_a_dado_de_baja_devuelve_422(
    cliente,
    ubicacion_prueba,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-PUT-BAJA-001"
    )

    respuesta = cliente.put(
        f"/equipos/{original['id']}",
        json={"estado_actual": "dado_de_baja"},
    )

    assert respuesta.status_code == 422
    assert cliente.get(f"/equipos/{original['id']}").json() == original


def test_eliminar_equipo_dado_de_baja_devuelve_409(
    cliente,
    ubicacion_prueba,
):
    original = crear_equipo_prueba(
        cliente, ubicacion_prueba, "TEST-DELETE-BAJA-001"
    )
    baja = cliente.post(f"/equipos/{original['id']}/baja").json()

    respuesta = cliente.delete(f"/equipos/{original['id']}")

    assert respuesta.status_code == 409
    assert cliente.get(f"/equipos/{original['id']}").json() == baja
