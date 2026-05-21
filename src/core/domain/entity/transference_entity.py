# src.core.domain.entity.transaction.transference_entity.py
from datetime import datetime
from decimal import Decimal
from core.domain.entity.account_entity import Account
from core.domain.entity.transaction_entity import Transaction
from core.domain.entity.credit_entity import Credit
from core.domain.entity.debit_entity import Debit
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType

class Transference(Transaction):
    """
    Representa uma transferência de valores entre duas contas distintas.
    """

    def __init__(
        self,
        *,
        id: int | None = None,
        operand: Account,
        counterparty: Account,
        type: TransactionType = TransactionType.TRANSFERENCE,
        amount: Decimal,
        timestamp: datetime | None = None
    ) -> None:
        super().__init__(
            id=id,
            operand=operand,
            counterparty=counterparty,
            type=type,
            amount=amount,
            timestamp=timestamp
        )


    def _operate(self) -> TransactionResult:
        """
        Executa a transferência orquestrando as operações unárias.
        """

        msg: str = f"{self.__class__.__name__} Operate:"
        debit = Debit|None
        credit = Credit|None

        try:
            debit = Debit(operand=self._operand, counterparty=self._counterparty, amount=self.amount)

            if debit.status == TransactionStatus.COMPLETED.value:

                credit = Credit(operand=self._counterparty,counterparty=self._operand, amount=self.amount)

                if credit.status == TransactionStatus.COMPLETED.value:

                    self._status = TransactionStatus.COMPLETED

                    msg += f"{self._type.value} realizado com sucesso"

        except Exception as e:
            self._status = TransactionStatus.FAILED

            try:

                if credit is not None and credit.status is TransactionStatus.FAILED.value:
                    Debit(operand=self._counterparty, counterparty=self._operand, amount=self.amount)

                if debit is not None and debit.status  is TransactionStatus.FAILED.value:
                    Credit(operand=self._counterparty, counterparty=self._operand,amount=self.amount)

                msg += f" Restorno Bem sucedido"
                self._status = TransactionStatus.REVERTED

            except Exception as revert_error:
                msg += f" Restorno falhou: {str(revert_error)}"

            msg += f"{self._type.value} falhou: {str(e)}"

        return self._build_result(self.status, f"{self.__class__.__name__}:{str(msg)}")
