from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

from database.base import Base
from database.db import DATABASE_URL

# Registrar todos los modelos en Base.metadata para el autogenerate.
import models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def obtener_url():
    # Los tests pasan su propia URL (biomaint_test); si no, se usa
    # la base de desarrollo definida en .env.
    return config.attributes.get("url", DATABASE_URL)


def run_migrations_offline() -> None:
    """Genera el SQL de las migraciones sin conectarse a la base."""
    context.configure(
        url=obtener_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Aplica las migraciones conectándose a la base."""
    connectable = create_engine(obtener_url(), poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
