import sys
import logging
from pathlib import Path
from logging.config import fileConfig

from sqlalchemy import  pool, create_engine
from alembic import context

# Garante que o diretório 'src' tenha prioridade no sys.path
BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR / "src") not in sys.path:
    sys.path.insert(0, str(BASE_DIR / "src"))

# Configurações e Tabelas
from infrastructure.config import settings  # type: ignore
from infrastructure.persistence.model.models_module import Base  # type: ignore

# Importe aqui todos os modelos para garantir que o Base.metadata os conheça
# Exemplo: from infrastructure.persistence.model import user_model, product_model

# Alembic Config object
config = context.config

if config.config_file_name:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

logger = logging.getLogger("alembic.env")

# SqlAlchemy - Criação automática de tabelas
target_metadata = Base.metadata

def get_url() -> str:
    """
    Retorna a URL síncrona definida na configuração do projeto.
    """
    return str(settings.ROOT_SYNC)

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""


    connectable = create_engine(
        get_url(),
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
