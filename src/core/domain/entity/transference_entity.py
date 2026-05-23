# src.core.domain.entity.transference_entity.py
from datetime import datetime
from decimal import Decimal
from typing import Self

from core.domain.entity.account_entity import Account
from core.domain.entity.credit_entity import Credit
from core.domain.entity.debit_entity import Debit
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType
from core.exception.entity.transaction.transaction_exception import InsufficientFundsException, InvalidAccount, SameAccountException


class Transference(Transaction):
    """
    Representa uma transferência de valores entre duas contas distintas.
    """
    _transaction_type: TransactionType = TransactionType.TRANSFERENCE

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
    #         transaction_type = self._transaction_type, # Usa o tipo definido na classe
    #         amount=amount,
    #         timestamp=timestamp
    #     )


    def _operate(self, account_orig: Account, account_dest: Account) -> TransactionResult:
            """
            Executa a transferência orquestrando as operações unárias.
            """

            msg: str = f"{self.__class__.__name__} Operate:"
            debit = Debit | None
            credit = Credit | None

            try:
                debit = Debit.create(account_orig=account_orig, account_dest=account_dest, amount=self.amount)

                if debit.status == TransactionStatus.COMPLETED.value:

                    credit = Credit.create(account_orig=account_orig, account_dest=account_dest, amount=self.amount)

                    if credit.status == TransactionStatus.COMPLETED.value:
                        self._status = TransactionStatus.COMPLETED

                        msg += f"{self.type} realizado com sucesso"

            except Exception as e:
                self._status = TransactionStatus.FAILED

                try:

                    if credit is not None and credit.status is TransactionStatus.FAILED.value:
                        Debit.create(account_orig=account_dest, account_dest=account_orig, amount=self.amount)

                    if debit is not None and debit.status is TransactionStatus.FAILED.value:
                        Credit.create(account_orig=account_dest, account_dest=account_orig, amount=self.amount)

                    msg += f" Restorno Bem sucedido"
                    self._status = TransactionStatus.REVERTED

                except Exception as revert_error:
                    msg += f" Restorno falhou: {str(revert_error)}"

                msg += f"{self._type.value} falhou: {str(e)}"

            return self._build_result(self.status, f"{self.__class__.__name__}:{str(msg)}")