"""Validaciones reutilizadas por varios schemas."""

from datetime import date

from schemas.estados import EstadoEquipo


def rechazar_null(valor):
    # Para campos obligatorios en un Update: pueden omitirse, pero no
    # enviarse como null (el validador solo corre si vienen en el body).
    if valor is None:
        raise ValueError("Este campo no puede ser nulo.")
    return valor


def rechazar_fecha_futura(fecha: date | None) -> date | None:
    if fecha is not None and fecha > date.today():
        raise ValueError("La fecha no puede ser futura.")
    return fecha


def rechazar_dado_de_baja(estado):
    if estado == EstadoEquipo.DADO_DE_BAJA:
        raise ValueError("Para dar de baja un equipo usá POST /equipos/{id}/baja.")
    return estado
