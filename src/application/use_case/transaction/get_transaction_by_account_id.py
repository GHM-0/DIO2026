from typing import Type

from application.dto.transaction_dto import TransactionResponse
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.repository.transaction_repository_interface import ITransactionRepository


class GetTransactionByAccountId:

    def __init__(self, uow: IAsyncDbTransactionUnit,
                 transaction_repo: Type[ITransactionRepository]):
        self._uow = uow
        self._transaction_repo = transaction_repo

    async def execute(self, account_id: int) -> list[TransactionResponse]:

        async with self._uow:
            repo = self._uow.get_repository(self._transaction_repo)
            transactions_recovered = await repo.get_all_by_account_id(account_id) or []

            return [
                TransactionResponse(
                    id=transaction.id,
                    timestamp=transaction.timestamp,
                    account_orig_id=transaction.account_orig_id,
                    account_dest_id=transaction.account_dest_id,
                    type=transaction.type,
                    amount=transaction.amount
                )
                for transaction in transactions_recovered
            ]