import asyncio
import importlib
import os
from logging.config import fileConfig

from alembic import context
from alembic.script import ScriptDirectory
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from config.database import Base
from config.settings import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# адрес базы берём из .env, а не из alembic.ini
config.set_main_option("sqlalchemy.url", get_settings().DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def import_submodules(directory: str, search: str = "models") -> None:
    """Импортирует всё, где в имени есть models, чтобы модели попали в Base.metadata."""
    for root, dirs, files in os.walk(directory):
        for file_ in files:
            if not file_.endswith(".py"):
                continue
            if search in file_:
                module = root.replace(os.sep, ".") + "." + file_[:-3]
                importlib.import_module(module)
        for dir_ in dirs:
            if search in dir_:
                module = root.replace(os.sep, ".") + "." + dir_
                importlib.import_module(module)


import_submodules("app")

# по этим метаданным Alembic строит миграции
target_metadata = Base.metadata


def process_revision_directives(context, revision, directives):
    """Нумеруем миграции 0001, 0002 и требуем описание через -m."""
    # нужен только для alembic revision, alembic check тоже сюда заходит, но описания у него нет
    if config.cmd_opts is None or config.cmd_opts.cmd[0].__name__ != "revision":
        return
    if not directives:
        return
    migration = directives[0]
    if not (migration.message or "").strip():
        raise SystemExit(
            'Provide a migration description: alembic revision -m "what changed"'
        )
    script_directory = ScriptDirectory.from_config(config)
    highest = 0
    for existing in script_directory.walk_revisions():
        if existing.revision.isdigit():
            highest = max(highest, int(existing.revision))
    migration.rev_id = f"{highest + 1:04d}"


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
