# src.core.domain.entity.transaction.credit_entity.py
import concurrent
from datetime import datetime
from decimal import Decimal
from core.domain.entity.account_entity import Account
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_type import TransactionType

class Credit(Transaction):
    """
    Representa uma operação unária de crédito.
    """

    def __init__(
        self,
        *,
        id: int | None = None,
        operand: Account,
        type: TransactionType = TransactionType.CREDIT,
        amount: Decimal,
        timestamp: datetime | None = None
    ) -> None:
        super().__init__(
            id=id,
            operand=operand,
            counterparty=operand,
            type=type,
            amount=amount,
            timestamp=timestamp
        )

    # Do not compute counterparty it-self
    def _operate(self) -> TransactionResult:
        msg:str = f"{self.__class__.__name__} Operate:"

        try:
            self._operand.deposit(self.amount)  # Se Não lançar uma Exceção

            self._status = True
            msg += f"{self._type.value} realizado com sucesso"

        except Exception as e:
            self._status = False
            msg += f"{self._type.value} falhou: {str(e)}"

        return self._build_result(True, msg)


















