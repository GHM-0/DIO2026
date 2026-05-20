from typing import Type

from application.dto.transaction_dto import TransactionResponse, CreateTransactionRequest
from core.domain.entity.transaction_entity import Transaction
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit
from core.domain.port.repository.transaction_repository_interface import ITransactionRepository
from core.domain.port.repository.account_repository_interface import IAccountRepository


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
            
            # 1. Reconstituição: Carrega conta origem
            account_orig = await account_repo.read_one(request.account_orig_id)
            if not account_orig:
                raise ValueError(f"Conta de origem {request.account_orig_id} não encontrada.")

            # 2. Reconstituição: Carrega conta destino (se houver e for diferente da origem)
            account_dest = None
            if request.account_dest_id and request.account_dest_id != request.account_orig_id:
                account_dest = await account_repo.read_one(request.account_dest_id)
                # A validação de existência da conta destino para transferência é feita dentro da Transaction.operate

            # 3. Criação da Entidade Transaction
            transaction_entity = Transaction(
                account_orig_id=request.account_orig_id,
                account_dest_id=request.account_dest_id,
                amount=request.amount, 
                type=request.type
            )

            # 4. Operação: A transação opera sobre as contas (Valida titularidade e Saldo)
            transaction_entity.operate(
                account_orig=account_orig,
                account_dest=account_dest,
                requester_user_id=requester_user_id
            )

            # 5. Persistência: Atualiza o estado das contas e salva a transação
            await account_repo.update_one(account_orig)
            if account_dest:
                await account_repo.update_one(account_dest)
                
            saved_transaction = await transaction_repo.save_one(transaction_entity)

            return TransactionResponse(
                id = saved_transaction.id,
                timestamp = saved_transaction.timestamp,
                account_orig_id = saved_transaction.account_orig_id,
                account_dest_id = saved_transaction.account_dest_id,
                type = saved_transaction.type,
                amount = saved_transaction.amount
            )