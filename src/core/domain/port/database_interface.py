# src.core.domain.port.database_interface.py
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, AsyncContextManager

E = TypeVar("E")

class IAsyncDatabase(ABC, Generic[E]):
    @abstractmethod
    async def connect(self) -> None: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def health_check(self) -> bool: ...

    @abstractmethod
    async def get_session(self) -> AsyncContextManager[E]: ...