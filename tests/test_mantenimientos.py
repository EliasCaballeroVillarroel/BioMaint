from datetime import date, timedelta

import pytest

MANANA = (date.today() + timedelta(days=1)).isoformat()

CAMPOS_MANTENIMIENTO = {
    "id",
    "equipo_id",
    "falla_id",
    "fecha",
    "tipo_mantenimiento",
    "duracion_mantenimiento",
    "descripcion",
    "resultado",
    "tecnico_ids",
}


@pytest.fixture
def falla_prueba(cliente, equipo_prueba):
    respuesta = cliente.post(
        "/fallas",
        json={
            "equipo_id": equipo_prueba["id"],
            "tipo_falla": "Electrica",
            "fecha_falla": "2025-03-10",
        },
    )
    assert respuesta.status_code == 201
    return respuesta.json()


@pytest.fixture
def crear_mantenimiento_api(cliente, equipo_prueba):
    # Por defecto crea un preventivo sobre el equipo de prueba.
    def crear(**datos):
        respuesta = cliente.post(
            "/mantenimientos",
            json={
                "equipo_id": equipo_prueba["id"],
                "fecha": "2025-04-01",
                "tipo_mantenimiento": "Preventivo",
                **datos,
            },
        )
        assert respuesta.status_code == 201, respuesta.json()
        return respuesta.json()

    return crear


# --- Crear ---


def test_crear_mantenimiento_preventivo_devuelve_formato_esperado(
    cliente,
    equipo_prueba,
):
    datos = {
        "equipo_id": equipo_prueba["id"],
        "fecha": "2025-04-01",
        "tipo_mantenimiento": "Preventivo",
        "duracion_mantenimiento": 90,
        "descripcion": "Inspeccion general.",
        "resultado": "Equipo operativo.",
    }

    respuesta = cliente.post("/mantenimientos", json=datos)

    assert respuesta.status_code == 201
    mantenimiento = respuesta.json()
    assert set(mantenimiento.keys()) == CAMPOS_MANTENIMIENTO
    assert mantenimiento == {
        **datos,
        "id": mantenimiento["id"],
        "falla_id": None,
        "tecnico_ids": [],
    }


def test_crear_mantenimiento_predictivo(crear_mantenimiento_api):
    mantenimiento = crear_mantenimiento_api(tipo_mantenimiento="Predictivo")

    assert mantenimiento["tipo_mantenimiento"] == "Predictivo"


def test_crear_mantenimiento_correctivo_con_falla(
    crear_mantenimiento_api,
    falla_prueba,
):
    mantenimiento = crear_mantenimiento_api(
        tipo_mantenimiento="Correctivo",
        falla_id=falla_prueba["id"],
        fecha="2025-03-12",
    )

    assert mantenimiento["falla_id"] == falla_prueba["id"]


def test_crear_mantenimiento_correctivo_el_mismo_dia_de_la_falla(
    crear_mantenimiento_api,
    falla_prueba,
):
    mantenimiento = crear_mantenimiento_api(
        tipo_mantenimiento="Correctivo",
        falla_id=falla_prueba["id"],
        fecha=falla_prueba["fecha_falla"],
    )

    assert mantenimiento["fecha"] == falla_prueba["fecha_falla"]


def test_crear_mantenimiento_con_fecha_futura_para_planificar(
    crear_mantenimiento_api,
):
    mantenimiento = crear_mantenimiento_api(fecha=MANANA)

    assert mantenimiento["fecha"] == MANANA


def test_crear_mantenimiento_con_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.post(
        "/mantenimientos",
        json={
            "equipo_id": 999999,
            "fecha": "2025-04-01",
            "tipo_mantenimiento": "Preventivo",
        },
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un equipo con ID 999999."}


def test_crear_mantenimiento_en_equipo_dado_de_baja_devuelve_409(
    cliente,
    equipo_prueba,
):
    cliente.post(f"/equipos/{equipo_prueba['id']}/baja")

    respuesta = cliente.post(
        "/mantenimientos",
        json={
            "equipo_id": equipo_prueba["id"],
            "fecha": "2025-04-01",
            "tipo_mantenimiento": "Preventivo",
        },
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": ("No se pueden registrar mantenimientos en un equipo dado de baja.")
    }


def test_crear_mantenimiento_con_falla_inexistente_devuelve_404(
    cliente,
    equipo_prueba,
):
    respuesta = cliente.post(
        "/mantenimientos",
        json={
            "equipo_id": equipo_prueba["id"],
            "falla_id": 999999,
            "fecha": "2025-04-01",
            "tipo_mantenimiento": "Correctivo",
        },
    )

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe una falla con ID 999999."}


def test_crear_mantenimiento_con_falla_de_otro_equipo_devuelve_422(
    cliente,
    ubicacion_prueba,
    falla_prueba,
):
    otro_equipo = cliente.post(
        "/equipos",
        json={
            "nombre": "Otro equipo",
            "ubicacion_id": ubicacion_prueba,
            "estado_actual": "activo",
        },
    ).json()

    respuesta = cliente.post(
        "/mantenimientos",
        json={
            "equipo_id": otro_equipo["id"],
            "falla_id": falla_prueba["id"],
            "fecha": "2025-04-01",
            "tipo_mantenimiento": "Correctivo",
        },
    )

    assert respuesta.status_code == 422
    assert respuesta.json() == {
        "detail": "La falla no pertenece al equipo del mantenimiento."
    }


@pytest.mark.parametrize(
    ("cambios", "detalle"),
    [
        (
            {"tipo_mantenimiento": "Correctivo"},
            "Un mantenimiento correctivo debe indicar la falla que atiende.",
        ),
        (
            {"tipo_mantenimiento": "Preventivo", "usar_falla": True},
            "Solo un mantenimiento correctivo puede tener una falla asociada.",
        ),
        (
            {"tipo_mantenimiento": "Predictivo", "usar_falla": True},
            "Solo un mantenimiento correctivo puede tener una falla asociada.",
        ),
        (
            {
                "tipo_mantenimiento": "Correctivo",
                "usar_falla": True,
                "fecha": "2025-03-09",
            },
            "El mantenimiento no puede ser anterior a la falla que atiende.",
        ),
    ],
)
def test_crear_mantenimiento_que_no_respeta_la_relacion_con_la_falla(
    cliente,
    equipo_prueba,
    falla_prueba,
    cambios,
    detalle,
):
    datos = {"equipo_id": equipo_prueba["id"], "fecha": "2025-04-01"}
    if cambios.pop("usar_falla", False):
        datos["falla_id"] = falla_prueba["id"]

    respuesta = cliente.post("/mantenimientos", json={**datos, **cambios})

    assert respuesta.status_code == 422
    assert respuesta.json() == {"detail": detalle}


@pytest.mark.parametrize(
    "cambios",
    [
        {"equipo_id": 0},
        {"fecha": None},
        {"tipo_mantenimiento": "CORRECTIVO"},
        {"tipo_mantenimiento": None},
        {"duracion_mantenimiento": 0},
        {"duracion_mantenimiento": -30},
        {"falla_id": 0},
    ],
)
def test_crear_mantenimiento_con_datos_invalidos_devuelve_422(
    cliente,
    equipo_prueba,
    cambios,
):
    datos = {
        "equipo_id": equipo_prueba["id"],
        "fecha": "2025-04-01",
        "tipo_mantenimiento": "Preventivo",
        **cambios,
    }

    respuesta = cliente.post("/mantenimientos", json=datos)

    assert respuesta.status_code == 422
    assert cliente.get(f"/equipos/{equipo_prueba['id']}/mantenimientos").json() == []


# --- Técnicos asignados ---


def test_asignar_tecnicos_a_mantenimiento(
    cliente,
    crear_mantenimiento_api,
    crear_tecnico_api,
):
    mantenimiento = crear_mantenimiento_api()
    tecnico_a = crear_tecnico_api(nombre="Ana")
    tecnico_b = crear_tecnico_api(nombre="Bruno")

    cliente.post(f"/mantenimientos/{mantenimiento['id']}/tecnicos/{tecnico_b['id']}")
    respuesta = cliente.post(
        f"/mantenimientos/{mantenimiento['id']}/tecnicos/{tecnico_a['id']}"
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["tecnico_ids"] == sorted([tecnico_a["id"], tecnico_b["id"]])

    asignados = cliente.get(f"/tecnicos/{tecnico_a['id']}/mantenimientos")
    assert [m["id"] for m in asignados.json()] == [mantenimiento["id"]]


def test_asignar_el_mismo_tecnico_dos_veces_no_lo_duplica(
    cliente,
    crear_mantenimiento_api,
    crear_tecnico_api,
):
    mantenimiento = crear_mantenimiento_api()
    tecnico = crear_tecnico_api()
    ruta = f"/mantenimientos/{mantenimiento['id']}/tecnicos/{tecnico['id']}"

    cliente.post(ruta)
    respuesta = cliente.post(ruta)

    assert respuesta.status_code == 200
    assert respuesta.json()["tecnico_ids"] == [tecnico["id"]]


def test_asignar_tecnico_inexistente_devuelve_404(
    cliente,
    crear_mantenimiento_api,
):
    mantenimiento = crear_mantenimiento_api()

    respuesta = cliente.post(f"/mantenimientos/{mantenimiento['id']}/tecnicos/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un técnico con ID 999999."}


def test_asignar_tecnico_a_mantenimiento_inexistente_devuelve_404(
    cliente,
    crear_tecnico_api,
):
    tecnico = crear_tecnico_api()

    respuesta = cliente.post(f"/mantenimientos/999999/tecnicos/{tecnico['id']}")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un mantenimiento con ID 999999."}


# --- Listar y consultar ---


def test_listar_mantenimientos_incluye_el_creado(
    cliente,
    crear_mantenimiento_api,
):
    mantenimiento = crear_mantenimiento_api()

    respuesta = cliente.get("/mantenimientos")

    assert respuesta.status_code == 200
    assert mantenimiento in respuesta.json()


def test_listar_mantenimientos_sin_registros_devuelve_lista_vacia(
    cliente,
    base_vacia,
):
    respuesta = cliente.get("/mantenimientos")

    assert respuesta.status_code == 200
    assert respuesta.json() == []


def test_consultar_mantenimiento_existente(cliente, crear_mantenimiento_api):
    mantenimiento = crear_mantenimiento_api()

    respuesta = cliente.get(f"/mantenimientos/{mantenimiento['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json() == mantenimiento


def test_consultar_mantenimiento_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/mantenimientos/999999")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "No existe un mantenimiento con ID 999999."}


def test_listar_mantenimientos_de_equipo_ordenados_por_fecha_descendente(
    cliente,
    equipo_prueba,
    ubicacion_prueba,
    crear_mantenimiento_api,
):
    antiguo = crear_mantenimiento_api(fecha="2024-01-10")
    reciente = crear_mantenimiento_api(fecha="2025-06-01")
    otro_equipo = cliente.post(
        "/equipos",
        json={
            "nombre": "Otro equipo",
            "ubicacion_id": ubicacion_prueba,
            "estado_actual": "activo",
        },
    ).json()
    cliente.post(
        "/mantenimientos",
        json={
            "equipo_id": otro_equipo["id"],
            "fecha": "2025-01-01",
            "tipo_mantenimiento": "Preventivo",
        },
    )

    respuesta = cliente.get(f"/equipos/{equipo_prueba['id']}/mantenimientos")

    assert respuesta.status_code == 200
    assert respuesta.json() == [reciente, antiguo]


def test_listar_mantenimientos_de_equipo_inexistente_devuelve_404(cliente):
    respuesta = cliente.get("/equipos/999999/mantenimientos")

    assert respuesta.status_code == 404


# --- Actualizar ---


@pytest.mark.parametrize(
    "cambios",
    [
        {"fecha": "2025-05-01"},
        {"duracion_mantenimiento": 45},
        {"descripcion": "Descripcion nueva."},
        {"resultado": "Equipo operativo."},
        {"tipo_mantenimiento": "Predictivo"},
        {"fecha": MANANA, "duracion_mantenimiento": 30},
    ],
)
def test_actualizar_mantenimiento(cliente, crear_mantenimiento_api, cambios):
    original = crear_mantenimiento_api()

    respuesta = cliente.put(f"/mantenimientos/{original['id']}", json=cambios)

    esperado = {**original, **cambios}
    assert respuesta.status_code == 200
    assert respuesta.json() == esperado
    assert cliente.get(f"/mantenimientos/{original['id']}").json() == esperado


def test_convertir_preventivo_en_correctivo_indicando_la_falla(
    cliente,
    crear_mantenimiento_api,
    falla_prueba,
):
    original = crear_mantenimiento_api()

    respuesta = cliente.put(
        f"/mantenimientos/{original['id']}",
        json={
            "tipo_mantenimiento": "Correctivo",
            "falla_id": falla_prueba["id"],
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["falla_id"] == falla_prueba["id"]


def test_convertir_correctivo_en_preventivo_quitando_la_falla(
    cliente,
    crear_mantenimiento_api,
    falla_prueba,
):
    original = crear_mantenimiento_api(
        tipo_mantenimiento="Correctivo",
        falla_id=falla_prueba["id"],
    )

    respuesta = cliente.put(
        f"/mantenimientos/{original['id']}",
        json={
            "tipo_mantenimiento": "Preventivo",
            "falla_id": None,
        },
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["falla_id"] is None


def test_actualizar_mantenimiento_sin_campos_devuelve_400(
    cliente,
    crear_mantenimiento_api,
):
    original = crear_mantenimiento_api()

    respuesta = cliente.put(f"/mantenimientos/{original['id']}", json={})

    assert respuesta.status_code == 400


def test_actualizar_mantenimiento_inexistente_devuelve_404(cliente):
    respuesta = cliente.put(
        "/mantenimientos/999999",
        json={"descripcion": "No existe"},
    )

    assert respuesta.status_code == 404


@pytest.mark.parametrize(
    "cambios",
    [
        {"fecha": None},
        {"tipo_mantenimiento": None},
        {"tipo_mantenimiento": "Mensual"},
        {"duracion_mantenimiento": 0},
        # Correctivo sin falla.
        {"tipo_mantenimiento": "Correctivo"},
        # Preventivo con falla.
        {"usar_falla": True},
    ],
)
def test_actualizar_preventivo_con_datos_invalidos_no_modifica_datos(
    cliente,
    crear_mantenimiento_api,
    falla_prueba,
    cambios,
):
    original = crear_mantenimiento_api()
    if cambios.pop("usar_falla", False):
        cambios["falla_id"] = falla_prueba["id"]

    respuesta = cliente.put(f"/mantenimientos/{original['id']}", json=cambios)

    assert respuesta.status_code == 422
    assert cliente.get(f"/mantenimientos/{original['id']}").json() == original


@pytest.mark.parametrize(
    "cambios",
    [
        # Quedaría antes que la falla que atiende.
        {"fecha": "2025-03-09"},
        # Un correctivo no puede quedarse sin falla.
        {"falla_id": None},
    ],
)
def test_actualizar_correctivo_con_datos_invalidos_no_modifica_datos(
    cliente,
    crear_mantenimiento_api,
    falla_prueba,
    cambios,
):
    original = crear_mantenimiento_api(
        tipo_mantenimiento="Correctivo",
        falla_id=falla_prueba["id"],
        fecha="2025-03-12",
    )

    respuesta = cliente.put(f"/mantenimientos/{original['id']}", json=cambios)

    assert respuesta.status_code == 422
    assert cliente.get(f"/mantenimientos/{original['id']}").json() == original


def test_actualizar_mantenimiento_con_falla_inexistente_devuelve_404(
    cliente,
    crear_mantenimiento_api,
):
    original = crear_mantenimiento_api()

    respuesta = cliente.put(
        f"/mantenimientos/{original['id']}",
        json={
            "tipo_mantenimiento": "Correctivo",
            "falla_id": 999999,
        },
    )

    assert respuesta.status_code == 404
    assert cliente.get(f"/mantenimientos/{original['id']}").json() == original


@pytest.mark.parametrize("resultado", [None, "", "   "])
def test_no_se_puede_quitar_el_resultado_de_un_mantenimiento_finalizado(
    cliente,
    crear_mantenimiento_api,
    resultado,
):
    original = crear_mantenimiento_api(resultado="Equipo operativo.")

    respuesta = cliente.put(
        f"/mantenimientos/{original['id']}",
        json={"resultado": resultado},
    )

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": "No se puede quitar el resultado de un mantenimiento registrado."
    }
    assert cliente.get(f"/mantenimientos/{original['id']}").json() == original

    # Así tampoco se puede volver a un estado borrable.
    assert cliente.delete(f"/mantenimientos/{original['id']}").status_code == 409


def test_se_puede_corregir_el_resultado_de_un_mantenimiento_finalizado(
    cliente,
    crear_mantenimiento_api,
):
    original = crear_mantenimiento_api(resultado="Equipo operativo.")

    respuesta = cliente.put(
        f"/mantenimientos/{original['id']}",
        json={"resultado": "Equipo operativo, se cambio un filtro."},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["resultado"] == ("Equipo operativo, se cambio un filtro.")


def test_se_puede_completar_un_mantenimiento_de_equipo_dado_de_baja(
    cliente,
    equipo_prueba,
    crear_mantenimiento_api,
):
    # La baja impide registrar mantenimientos nuevos, no completar los
    # que ya existían.
    original = crear_mantenimiento_api()
    cliente.post(f"/equipos/{equipo_prueba['id']}/baja")

    respuesta = cliente.put(
        f"/mantenimientos/{original['id']}",
        json={"resultado": "Equipo retirado de servicio."},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["resultado"] == "Equipo retirado de servicio."


def test_un_put_parcial_no_revalida_la_relacion_con_la_falla(
    cliente,
    equipo_prueba,
):
    # Simula un registro cargado antes de las reglas de T7: un
    # correctivo sin falla, insertado directamente en la base.
    from base_pruebas import SesionPruebas
    from models import Mantenimiento

    with SesionPruebas() as session:
        viejo = Mantenimiento(
            equipo_id=equipo_prueba["id"],
            fecha=date(2024, 1, 10),
            tipo_mantenimiento="Correctivo",
        )
        session.add(viejo)
        session.commit()
        viejo_id = viejo.id

    respuesta = cliente.put(
        f"/mantenimientos/{viejo_id}",
        json={"descripcion": "Dato historico."},
    )

    assert respuesta.status_code == 200
    assert respuesta.json()["descripcion"] == "Dato historico."

    # Si cambia algo de la relación, sí se valida.
    respuesta = cliente.put(
        f"/mantenimientos/{viejo_id}",
        json={"fecha": "2024-01-11"},
    )
    assert respuesta.status_code == 422


# --- Eliminar ---


def test_eliminar_mantenimiento_sin_resultado_quita_sus_tecnicos(
    cliente,
    crear_mantenimiento_api,
    crear_tecnico_api,
):
    mantenimiento = crear_mantenimiento_api()
    tecnico = crear_tecnico_api()
    cliente.post(f"/mantenimientos/{mantenimiento['id']}/tecnicos/{tecnico['id']}")

    respuesta = cliente.delete(f"/mantenimientos/{mantenimiento['id']}")

    assert respuesta.status_code == 204
    assert cliente.get(f"/mantenimientos/{mantenimiento['id']}").status_code == 404

    # El técnico sigue existiendo, pero sin la asignación.
    assert cliente.get(f"/tecnicos/{tecnico['id']}").status_code == 200
    assert cliente.get(f"/tecnicos/{tecnico['id']}/mantenimientos").json() == []


@pytest.mark.parametrize("resultado", ["Equipo operativo.", "  Hecho  "])
def test_eliminar_mantenimiento_con_resultado_devuelve_409(
    cliente,
    crear_mantenimiento_api,
    resultado,
):
    mantenimiento = crear_mantenimiento_api(resultado=resultado)

    respuesta = cliente.delete(f"/mantenimientos/{mantenimiento['id']}")

    assert respuesta.status_code == 409
    assert respuesta.json() == {
        "detail": (
            "No se puede eliminar un mantenimiento con resultado registrado: "
            "forma parte del historial."
        )
    }
    assert cliente.get(f"/mantenimientos/{mantenimiento['id']}").json() == mantenimiento


def test_eliminar_mantenimiento_inexistente_devuelve_404(cliente):
    respuesta = cliente.delete("/mantenimientos/999999")

    assert respuesta.status_code == 404
