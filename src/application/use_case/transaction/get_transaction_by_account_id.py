# src.application.use_case.transaction.get_transaction_by_account_id.py
from datetime import datetime
from typing import Type, cast

from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.transaction_dto import TransactionResponse
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.repository.transaction_repository_interface import ITransactionRepository


class GetTransactionByAccountId:

    def __init__(self, uow: IAsyncDbTransactionUnit[AsyncSession],
                 transaction_repo: Type[ITransactionRepository]):
        self._uow = uow
        self._transaction_repo = transaction_repo

    async def execute(self, account_id: int, limit: int|None=None, skip: int|None= None) -> list[TransactionResponse]:

        async with self._uow:
            repo = self._uow.get_repository(self._transaction_repo)


            if limit is not None and skip is not None:
                transactions_recovered = await repo.get_all_by_account_id_paginated(account_id, limit, skip)

            else:
                transactions_recovered = await repo.get_all_by_account_id(account_id)

            return [
                # TransactionResponse(
                #     id=cast(int,transaction.id),
                #     timestamp=cast(datetime,transaction.timestamp),
                #     account_orig_id=transaction.account_orig_id,
                #     account_dest_id=transaction.account_dest_id,
                #     type=transaction.type,
                #     amount=transaction.amount,
                #     status=transaction.status
                # )
                TransactionResponse.model_validate(transaction)
                for transaction in transactions_recovered
            ]