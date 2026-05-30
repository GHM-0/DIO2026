# src.application.use_case.transaction.get_transaction_by_id.py
from datetime import datetime
from typing import Type, cast

from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.transaction_dto import TransactionResponse
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.repository.transaction_repository_interface import ITransactionRepository


class GetTransactionById:

    def __init__(self, uow: IAsyncDbTransactionUnit[AsyncSession],
                 transaction_repo: Type[ITransactionRepository]):
        self._uow = uow
        self._transaction_repo = transaction_repo

    # Recuperação de uma Account por ID
    async def execute(self, transaction_id: int) -> TransactionResponse | None:

        async with self._uow:
            repo = self._uow.get_repository(self._transaction_repo)

            transaction_recovered = await repo.read_one(transaction_id)

            if not transaction_recovered or transaction_recovered.is_persisted() == False:
                return None

            return TransactionResponse(
                id = cast(int,transaction_recovered.id),
                timestamp = cast(datetime,transaction_recovered.timestamp),
                account_orig_id = transaction_recovered.account_orig_id,
                account_dest_id = transaction_recovered.account_dest_id,
                type = transaction_recovered.type,
                amount = transaction_recovered.amount,
                status = transaction_recovered.status,
                message = transaction_recovered.message
            )