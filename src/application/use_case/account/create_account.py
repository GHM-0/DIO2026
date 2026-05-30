# src.application.use_case.account.create_account.py

from datetime import datetime
from typing import Type, cast

from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.account_dto import AccountResponse, CreateAccountRequest
from core.domain.entity.account_entity import Account
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.repository.account_repository_interface import IAccountRepository

class CreateAccount:

    def __init__(self, uow: IAsyncDbTransactionUnit[AsyncSession], repo_class: Type[IAccountRepository]):
        self._uow = uow
        self._repo = repo_class

    async def execute(self, request: CreateAccountRequest) -> AccountResponse:
        async with self._uow:

            repository = self._uow.get_repository(self._repo)

            account_entity = Account(user_id=request.user_id, balance=request.balance)
            saved_account = await repository.save_one(account_entity)

            return AccountResponse(
                id=cast(int,saved_account.id),
                user_id=saved_account.user_id,
                balance=saved_account.balance,
                created_at=cast(datetime,saved_account.created_at)
            )