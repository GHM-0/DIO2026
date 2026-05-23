from typing import Type

from application.dto.transaction_dto import TransactionResponse, CreateTransactionRequest
from core.domain.entity.account_entity import Account
from core.domain.entity.credit_entity import Credit
from core.domain.entity.debit_entity import Debit
from core.domain.entity.transference_entity import Transference
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.repository.transaction_repository_interface import ITransactionRepository
from core.domain.port.repository.account_repository_interface import IAccountRepository
from core.domain.value_object.transaction_type import TransactionType

from application.use_case.exception.create_transaction_exception import (TransactionNaoPodeSerCriadoException,
UserNotAuthorizedException)

class CreateTransaction:

    def __init__(self, uow: IAsyncDbTransactionUnit,
                 transaction_repo: Type[ITransactionRepository],
                 account_repo: Type[IAccountRepository]):
        self._uow = uow
        self._transaction_repo = transaction_repo
        self._account_repo = account_repo

    async def execute(self, request: CreateTransactionRequest, requester_user_id: int) -> TransactionResponse:
        """
        Executa a transação reconstituindo as contas e delegando a operação para a entidade Transaction.
        """
        async with self._uow:
            transaction_repo = self._uow.get_repository(self._transaction_repo)
            account_repo = self._uow.get_repository(self._account_repo)

            account_orig: Account|None = await account_repo.read_one(request.account_orig_id)
            if not account_orig:
                raise ValueError(f"Conta de origem {request.account_orig_id} não encontrada.")

            if account_orig.user_id != requester_user_id:
                raise UserNotAuthorizedException("Usuário não autorizado a operar nesta conta de origem.")

            account_dest: Account|None = await account_repo.read_one(request.account_dest_id)
            if not account_dest:
                raise ValueError(f"Conta destino {request.account_dest_id} não encontrada.")

            try:

                transaction_map = {
                    TransactionType.TRANSFERENCE.value: Transference,
                    TransactionType.CREDIT.value: Credit,
                    TransactionType.DEBIT.value: Debit,
                }

                transaction_class = transaction_map[request.type.value]
                transaction = transaction_class.create(
                    account_orig=account_orig,
                    account_dest=account_dest,
                    amount=request.amount,
                )

                # Try
                await account_repo.update_one(account_orig)
                await account_repo.update_one(account_dest)
                # Qualquer erro aqui Será revertido por uow

                transaction_saved = await transaction_repo.save_one(transaction)

            except Exception as e:
                raise TransactionNaoPodeSerCriadoException(
                    f"Erro: {str(e)}"
                )

            return TransactionResponse(
                id = transaction_saved.id,
                timestamp = transaction_saved.timestamp,
                account_orig_id = transaction_saved.account_orig_id,
                account_dest_id = transaction_saved.account_dest_id,
                type = transaction_saved.type,
                amount = transaction_saved.amount
            )