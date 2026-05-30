# src.core.domain.entity.transference_entity.py

from core.domain.entity.account_entity import Account
from core.domain.entity.credit_entity import Credit
from core.domain.entity.debit_entity import Debit
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType

class Transference(Transaction):
    """
    Representa uma transferência de valores entre duas contas distintas.
    """
    _transaction_type: TransactionType = TransactionType.TRANSFERENCE

    def _operate(self, account_orig: Account, account_dest: Account) -> TransactionResult:
            """
            Executa a transferência orquestrando as operações unárias.
            """

            self._message: str = f"{self.__class__.__name__} Operate:"
            debit:Debit|None = None
            credit:Credit|None = None


            debit = Debit.create(account_orig=account_orig, account_dest=account_dest, amount=self.amount)

            if debit is not None and debit.status == TransactionStatus.COMPLETED:

                credit = Credit.create(account_orig=account_orig, account_dest=account_dest, amount=self.amount)

                if credit is not None and credit.status == TransactionStatus.COMPLETED:
                    self._status = TransactionStatus.COMPLETED

                    self._message += f"{self.type} realizado com sucesso"

            else:
                self._status = TransactionStatus.FAILED

                try:

                    if credit is not None and credit.status is TransactionStatus.FAILED:
                        Debit.create(account_orig=account_dest, account_dest=account_orig, amount=self.amount)

                    if debit is not None and debit.status is TransactionStatus.FAILED:
                        Credit.create(account_orig=account_dest, account_dest=account_orig, amount=self.amount)

                        self._message += f" Estorno Bem sucedido"
                        self._status = TransactionStatus.REVERTED

                except Exception as revert_error:
                    self._message += f" Estorno falhou: {str(revert_error)}"

                self._message += f"{self.type.value} falhou: {str(self.message)}" # Linha corrigida aqui

            return self._build_result()