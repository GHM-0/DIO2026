from typing import Type

from application.dto.account_dto import AccountResponse
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.repository.account_repository_interface import IAccountRepository

class GetAccountsByUserId:

    def __init__(self, uow: IAsyncDbTransactionUnit, repo_class: Type[IAccountRepository]):
        self._uow = uow
        self._repo = repo_class

    # Recuperação de uma Account por User_ID com ou sem limit/paggination
    async def execute(self,user_id:int, limit: int|None, skip: int|None) -> list[AccountResponse]:

        async with self._uow:
            repository = self._uow.get_repository(self._repo)

            if limit is not None and skip is not None:
                accounts_recovered = await repository.get_all_by_user_id_paginated(user_id, limit, skip)

            else:
                accounts_recovered = await repository.get_all_by_user_id(user_id)

            return [AccountResponse.model_validate(acc) for acc in accounts_recovered]