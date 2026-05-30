# src.core.domain.port.repository_interface.py

from abc import ABC,abstractmethod
from typing import List, TypeVar, Generic, Optional, Dict, Any

T = TypeVar("T")

class IRepository(ABC, Generic[T]):
    """
    Interface Genérica para operações de persistência.
    Utilizada para todas as entidades do domínio.
    """

    # Sugestão do Gemini Para atender a requisitos do mypy
    @abstractmethod
    def __init__(self, session: Any) -> None: # Adicionado: Contrato de inicialização
        """
        Inicializa o repositório com uma sessão.
        As implementações concretas devem aceitar o tipo de sessão apropriado.
        """
        ...

    @abstractmethod
    async def read_all(self) -> List[T]:
        """Busca todos os registros."""
        ...

    @abstractmethod
    async def read_all_paginated(self, limit: int, skip: int) -> List[T]:
        """Busca todos os registros com paginação"""
        ...

    @abstractmethod
    async def exists_by_id(self, id: int) -> bool:
        """Verifica existência de forma otimizada."""
        ...

    @abstractmethod
    async def read_one(self, id: int) -> Optional[T]:
        """Recupera uma única entidade pelo ID."""
        ...

    @abstractmethod
    async def save_one(self, entity: T) -> T:
        """Persiste o estado de uma entidade."""
        ...

    # @abstractmethod
    # async def update_one(self, transaction_id: int, changes: Dict[str, Any]) -> Optional[T]:
    #     """Aplica atualizações parciais."""
    #     ...

    @abstractmethod
    async def update_one(self, entity:T) -> Optional[T]:
        """Aplica atualizações parciais."""
        ...

    # Uma transação não é retratável, sua reversão se dá por outra de mesmo valor em sentido o posto
    @abstractmethod
    async def remove_one(self, id: int) -> bool:
        """Exclui permanentemente um registro."""
        ...

    # Não serão implementados para este exercício
    # @abstractmethod
    # async def soft_delete_one(self, transaction_id: int) -> bool:
    #     """Exclusão lógica de um único registro."""
    #     ...
    #
    # @abstractmethod
    # async def soft_delete_many(self, ids: List[int]) -> int:
    #     """Exclusão lógica de múltiplos registros. Retorna a contagem de afetados."""
    #     ...
    #
    # @abstractmethod
    # async def save_many(self, entities: List[T]) -> List[T]:
    #     """Persiste múltiplas entidades em lote."""
    #     ...
    #
    # @abstractmethod
    # async def remove_many(self, ids: List[int]) -> int:
    #     """Exclui permanentemente múltiplos registros. Retorna a contagem de afetados."""
    #     ...
