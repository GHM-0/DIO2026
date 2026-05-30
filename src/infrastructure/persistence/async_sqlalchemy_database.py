# src.infrastructure.persistence.async_sqlalchemy_database.py

from contextlib import asynccontextmanager

# SQLAchy
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine, AsyncEngine

from typing import AsyncGenerator, Optional

# Interface IDatabase
from core.domain.port.database_interface import IAsyncDatabase


# Cria a sessão com o Banco de Dados de Maneira Assíncrona
class AsyncSqlAlchemyDatabase(IAsyncDatabase[AsyncSession]):
    """
    Asynchronous  connection manager for MySQL using SQLAlchemy

    Implements:IDatabase

    Args:
        database_url (str): The connection string (e.g., 'mysql+aiomysql://user:pass@host/db').
    """

    def __init__(self, database_url: str):
        self._url: str = database_url
        self._engine: Optional[AsyncEngine] = None
        self._session_factory:  Optional[async_sessionmaker[AsyncSession]] = None

    # Life cycle
    async def connect(self) -> None:
        """
        Cria a Conexão Assíncrona com SGBD por default não expira
        """
        if not self._engine:
            self._engine = create_async_engine(self._url)
            self._session_factory = async_sessionmaker(
                bind=self._engine,
                expire_on_commit=False
            )

    async def disconnect(self) -> None:
        """
        Desconecta o SGBD
        """
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None


    # Session factory
    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        """
        Retorna uma sessão válida com SGBD
        """
        if not self._session_factory:
            raise RuntimeError("Database não Conectada. Tente connect()")

        async with self._session_factory() as session:
            try:
                yield session
            finally:
                await session.close()

    # Auxiliary function
    async def health_check(self) -> bool:
        """
        Checa a conectividade com SGBD
        """
        if not self._engine:
            return False

        async with self._engine.connect() as conn:
            await conn.execute(sa.text("SELECT 1"))

        return True