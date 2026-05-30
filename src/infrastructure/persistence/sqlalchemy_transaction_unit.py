# src.infrastructure.persistence.sqlalchemy_transaction_unit.py
from typing import Optional, Type, Dict, TypeVar, AsyncContextManager, Any, cast, Callable
from sqlalchemy.ext.asyncio import AsyncSession

from types import TracebackType

from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.database_interface import IAsyncDatabase
from core.domain.port.repository.repository_interface import IRepository

R = TypeVar("R", bound=IRepository[Any])

class AsyncSqlAlchemyTransactionUnit(IAsyncDbTransactionUnit[AsyncSession]):
    """
    Implementação concreta da Unidade de Trabalho (UoW) para SQLAlchemy.
    Gerencia o ciclo de vida da sessão e garante a atomicidade.
    """

    def __init__(self, db: IAsyncDatabase[AsyncSession]) -> None:
        self._db = db
        self._session: Optional[AsyncSession] = None
        self._session_manager: Optional[AsyncContextManager[AsyncSession]] = None
        self._repositories: Dict[Type[IRepository[Any]], IRepository[Any]] = {}

    # Conexão assíncrona
    async def __aenter__(self) -> AsyncSqlAlchemyTransactionUnit:

        self._session_manager = self._db.get_session()
        self._session = await self._session_manager.__aenter__()

        return self

    #async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
    async def __aexit__(self, exc_type: Optional[Type[BaseException]], exc_val: Optional[BaseException],exc_tb: Optional[TracebackType]) -> None:
        try:
            if exc_type is None:
                await self.commit()
            else:
                await self.rollback()
        finally:

            if self._session_manager:
                await self._session_manager.__aexit__(exc_type, exc_val, exc_tb)

            self._session = None
            self._session_manager = None
            self._repositories.clear()

    def get_repository(self, repo_class: Type[R]) -> R:
        """
        Retorna uma instância do repositório injetando a sessão ativa.
        Utiliza cache interno para garantir singleton por transação.
        """
        if self._session is None:
            raise RuntimeError("Transação não iniciada. Utilize o contexto 'async with'.")

        if repo_class not in self._repositories:

            self._repositories[repo_class] = repo_class(self._session)

        #if repo_class not in self._repositories:

        #    repo_constructor: Callable[[AsyncSession], R] = cast(Callable[[AsyncSession], R], repo_class)
        #    self._repositories[repo_class] = repo_constructor(self._session)

        #return self._repositories[repo_class]
        return cast(R, self._repositories[repo_class])

    async def commit(self) -> None:
        if self._session:
            await self._session.commit()

    async def rollback(self) -> None:
        if self._session:

            try:
                await self._session.rollback()

            except Exception as e:
                raise RuntimeError(f"Falha ao Executar rollback:{str(e)}")
