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


def test_eliminar_ubicacion_con_equipos_devuelve_409(
    cliente,
    crear_ubicacion_api,
):
    ubicacion = crear_ubicacion_api()
    equipo = cliente.post("/equipos", json={
        "nombre": "Equipo asociado",
        "ubicacion_id": ubicacion["id"],
        "estado_actual": "activo",
    })
    assert equipo.status_code == 201

    respuesta = cliente.delete(f"/ubicaciones/{ubicacion['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede eliminar la ubicación porque tiene equipos asociados."
        )
    }
    assert cliente.get(f"/ubicaciones/{ubicacion['id']}").status_code == 200


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


def test_eliminar_ubicacion_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/ubicaciones/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {
        "detail": "No existe una ubicación con ID 999999."
    }
