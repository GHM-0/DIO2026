from typing import Type

from application.dto.account_dto import AccountResponse
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit

from core.domain.port.repository.account_repository_interface import IAccountRepository

class GetAccountByID:

    def __init__(self, uow: IAsyncDbTransactionUnit, repo_class: Type[IAccountRepository]):
        self._uow = uow
        self._repo = repo_class

    async def execute(self,account_id:int) -> AccountResponse|None:
        async with self._uow:
            repository = self._uow.get_repository(self._repo)

            account_recovered = await repository.read_one(account_id)

            if not account_recovered:
                return None

            return AccountResponse(
                id = account_recovered.id,
                user_id = account_recovered.user_id,
                balance = account_recovered.balance,
                created_at = account_recovered.created_at
            )