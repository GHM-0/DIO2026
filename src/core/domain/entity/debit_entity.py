# src.core.domain.entity.debit_entity.py
from datetime import datetime
from decimal import Decimal
from typing import Self

from core.domain.entity.account_entity import Account
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType
from core.exception.entity.transaction.transaction_exception import InsufficientFundsException, InvalidAccount


class Debit(Transaction):
    """
    Representa uma operação unária de débito.
    """

    _transaction_type: TransactionType = TransactionType.DEBIT

    # def __init__(
    #     self,
    #     *,
    #     id: int | None = None,
    #     account_orig_id: int, # Recebe o ID
    #     account_dest_id: int, # Recebe o ID
    #     amount: Decimal,
    #     timestamp: datetime | None = None
    # ) -> None:
    #     super().__init__(
    #         id=id,
    #         account_orig_id=account_orig_id, # Passa o ID para a classe base
    #         account_dest_id=account_dest_id, # Passa o ID para a classe base
    #         transaction_type=self._transaction_type,
    #         amount=amount,
    #         timestamp=timestamp
    #     )

    def _operate(self, account_orig: Account, account_dest: Account) -> TransactionResult:
        msg:str = f"{self.__class__.__name__} Operate:"

        if account_orig.id != self.account_orig_id:
            raise InvalidAccount(f"{msg} ID da conta de origem fornecido ({account_orig.id}) não corresponde ao da transação ({self.account_orig_id}).")

        try:
            account_orig.withdraw(self.amount)
            self._status = TransactionStatus.COMPLETED
            return self._build_result(self.status, f"{msg} Débito de {self.amount} da conta {account_orig.id} concluído com sucesso.")
        except InsufficientFundsException as e:
            self._status = TransactionStatus.FAILED
            return self._build_result(self.status, f"{msg} Falha ao debitar da conta {account_orig.id}. Erro: {str(e)}")