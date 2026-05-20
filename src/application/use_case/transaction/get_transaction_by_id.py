from typing import Type

from application.dto.transaction_dto import TransactionResponse
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.repository.transaction_repository_interface import ITransactionRepository


class GetTransactionById:

    def __init__(self, uow: IAsyncDbTransactionUnit,
                 transaction_repo: Type[ITransactionRepository]):
        self._uow = uow
        self._transaction_repo = transaction_repo

    # Recuperação de uma Account por ID
    async def execute(self, id: int) -> TransactionResponse | None:

        async with self._uow:
            repo = self._uow.get_repository(self._transaction_repo)

            transaction_recovered = await repo.read_one(id)

            if not transaction_recovered:
                return None

            return TransactionResponse(
                id = transaction_recovered.id,
                timestamp = transaction_recovered.timestamp,
                account_id = transaction_recovered.account_id,
                type = transaction_recovered.type,
                amount = transaction_recovered.amount
            )