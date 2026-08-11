from __future__ import annotations

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine

from alembic import context
import os

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import target metadata from app. Only routers/model modules that have been
# imported register their tables on Base.metadata — importing app.main pulls
# in every router (and therefore every model) the same way the running app
# does, so autogenerate sees the full schema rather than the handful of
# models app.models.__init__ re-exports directly.
import app.main  # noqa: F401  (import side effect: registers all models)
from app.db.session import Base

target_metadata = Base.metadata


def get_url() -> str:
    # Prefer env var, fallback to settings (which reads backend/.env), then alembic.ini
    if os.getenv("ALEMBIC_DATABASE_URL"):
        return os.getenv("ALEMBIC_DATABASE_URL")
    try:
        from app.core.config import settings
        return settings.DATABASE_URL_SYNC
    except Exception:
        return config.get_main_option("sqlalchemy.url")


def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = create_engine(get_url(), poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
