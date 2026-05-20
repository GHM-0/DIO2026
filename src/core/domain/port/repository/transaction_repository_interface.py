from abc import ABC, abstractmethod
from typing import List

from core.domain.entity.transaction_entity import Transaction
from core.domain.port.repository.repository_interface import IRepository


class ITransactionRepository(IRepository, ABC):

    @abstractmethod
    async def get_all_by_account_id(self, account_id: int) -> List[Transaction]:
        ...

    @abstractmethod
    async def get_all_by_account_id_paginated(self, account_id: int, limit: int, skip: int) -> List[Transaction]:
        ...