# src.application.use_case.account.get_account_by_id.py

from datetime import datetime
from typing import Type, cast

from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.account_dto import AccountResponse
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit

from core.domain.port.repository.account_repository_interface import IAccountRepository

class GetAccountByID:

    def __init__(self, uow: IAsyncDbTransactionUnit[AsyncSession], repo_class: Type[IAccountRepository]):
        self._uow = uow
        self._repo = repo_class

    async def execute(self,account_id:int) -> AccountResponse|None:
        async with self._uow:
            repository = self._uow.get_repository(self._repo)

            account_recovered = await repository.read_one(account_id)

            if not account_recovered or account_recovered.is_persisted() == False:
                return None

            return AccountResponse(
                id = cast(int,account_recovered.id),
                user_id = account_recovered.user_id,
                balance = account_recovered.balance,
                created_at = cast(datetime,account_recovered.created_at)
            )