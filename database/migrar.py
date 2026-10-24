"""
Aplica las migraciones de Alembic desde Python.

Desde la terminal el equivalente es:
    alembic upgrade head
"""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import URL

RAIZ_PROYECTO = Path(__file__).resolve().parent.parent

# Esquema anterior a Alembic (database/migraciones/versions).
REVISION_INICIAL = "cced584ed885"


def config_alembic(url: URL | str | None = None) -> Config:
    config = Config(str(RAIZ_PROYECTO / "alembic.ini"))

    # Sin URL, env.py usa la base de desarrollo definida en .env.
    if url is not None:
        config.attributes["url"] = url

    return config


def migrar(url: URL | str | None = None) -> None:
    command.upgrade(config_alembic(url), "head")
