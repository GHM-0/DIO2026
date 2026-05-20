from abc import ABC, abstractmethod
from typing import List

from core.domain.entity.account_entity import Account
from core.domain.port.repository.repository_interface import IRepository


class IAccountRepository(IRepository,ABC):

    @abstractmethod
    async def get_all_by_user_id(self, user_id: int) -> List[Account]:
        ...

    @abstractmethod
    async def get_all_by_user_id_paginated(self, user_id: int, limit: int, skip: int) -> List[Account]:
        ...
