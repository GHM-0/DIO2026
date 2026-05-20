# src.core.domain.port.async_db_transaction_unit_interface.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Type, Any

from core.domain.port.repository.repository_interface import IRepository

R = TypeVar("R", bound=IRepository)
T = TypeVar("T")

class IAsyncDbTransactionUnit(ABC, Generic[T]):
    """
        Gerencia a atomicidade de transações em um DB Async.
        Orquestra transações em repositórios sob um único contexto.
    """

    @abstractmethod
    def get_repository(self, repo_class: Type[R]) -> R:
        """
        Retorna uma instância do repositório solicitado,
        injetando automaticamente a sessão ativa desta unidade.
        """
        ...

    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...


    @abstractmethod
    async def __aenter__(self) -> "IAsyncDbTransactionUnit[T]": ...

    @abstractmethod
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None: ...
