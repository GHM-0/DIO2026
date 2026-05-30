# src.core.domain.entity.debit_entity.py

from core.domain.entity.account_entity import Account
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType
from exception.core.exception.entity.transaction.transaction_exception import InsufficientFundsException, InvalidAccount


class Debit(Transaction):
    """
    Representa uma operação unária de débito.
    """

    _transaction_type: TransactionType = TransactionType.DEBIT

    def _operate(self, account_orig: Account, account_dest: Account) -> TransactionResult:
        self._message:str = f"{self.__class__.__name__} Operate:"

        if account_orig.id != self.account_orig_id:
            raise InvalidAccount(f"{self._message} ID da conta de origem fornecido ({account_orig.id}) não corresponde ao da transação ({self.account_orig_id}).")

        try:
            account_orig.withdraw(self.amount)
            self._status = TransactionStatus.COMPLETED
            self._message += f" Débito de {self.amount} da conta {account_orig.id} concluído com sucesso."
            return self._build_result()
        except InsufficientFundsException as e:
            self._status = TransactionStatus.FAILED

            self._message += f" Falha ao debitar da conta {account_orig.id}. Erro: {str(e)}."
            return self._build_result()
