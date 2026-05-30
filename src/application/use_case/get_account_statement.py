# src.application.use_case.get_account_statement.py
from datetime import datetime
from typing import Type, cast

from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.account_dto import AccountResponse
from application.dto.transaction_dto import TransactionResponse

from application.dto.account_statement_dto import AccountStatementResponse
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit

from core.domain.port.repository.account_repository_interface import IAccountRepository
from core.domain.port.repository.transaction_repository_interface import ITransactionRepository


class GetAccountStatement:

    def __init__(self, uow: IAsyncDbTransactionUnit[AsyncSession],
                 account_repo: Type[IAccountRepository],
                 transaction_repo: Type[ITransactionRepository]):
        self._uow = uow
        self._account_repo = account_repo
        self._transaction_repo = transaction_repo

    async def execute(self, account_id: int, limit: int|None, skip: int|None) -> AccountStatementResponse:

        async with self._uow:

            account_repository = self._uow.get_repository(self._account_repo)
            transaction_repository = self._uow.get_repository(self._transaction_repo)

            account = await account_repository.read_one(account_id)

            if not account:
                raise ValueError(f"Conta com ID {account_id} não encontrada.")

            if limit is not None and skip is not None:
                transactions_recovered = await transaction_repository.get_all_by_account_id_paginated(account_id, limit,skip)
            else:
                transactions_recovered = await transaction_repository.get_all_by_account_id(account_id)

            account_dto = AccountResponse(
                id = cast(int,account.id),
                user_id = account.user_id,
                balance = account.balance,
                created_at = cast(datetime,account.created_at)
            )

            transactions_dto = [
                TransactionResponse(
                    id = cast(int,transaction.id),
                    account_orig_id = transaction.account_orig_id,
                    account_dest_id = transaction.account_dest_id,
                    amount = transaction.amount,
                    type = transaction.type,
                    timestamp = cast(datetime,transaction.timestamp),
                    status = transaction.status
                ) for transaction in transactions_recovered
            ]

            return AccountStatementResponse(
                account=account_dto,
                transactions=transactions_dto
            )