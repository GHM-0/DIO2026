# src.core.domain.entity.credit_entity.py

from core.domain.entity.account_entity import Account
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType
from exception.core.exception.entity.transaction.transaction_exception import InvalidAccount


class Credit(Transaction):
    """
    Representa uma operação unária de crédito.
    """
    _transaction_type: TransactionType = TransactionType.CREDIT

    def _operate(self, account_orig: Account, account_dest: Account) -> TransactionResult:
        self._message:str = f"{self.__class__.__name__} Operate:"


        if account_dest.id != self.account_dest_id:
            raise InvalidAccount(f"{self._message} ID da conta de destino fornecido ({account_dest.id}) não corresponde ao da transação ({self.account_dest_id}).")

        try:
            account_dest.deposit(self.amount)
            self._status = TransactionStatus.COMPLETED
            self._message += f"Crédito de {self.amount} na conta {account_dest.id} concluído com sucesso."
            return self._build_result()

        except Exception as e:
            self._status = TransactionStatus.FAILED
            self._message += f"{self._message} Falha ao creditar na conta {account_dest.id}. Erro: {str(e)}"
            return self._build_result()