# src.core.domain.entity.transaction.credit_entity.py
import concurrent
from datetime import datetime
from decimal import Decimal
from core.domain.entity.account_entity import Account
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
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
        counterparty: Account,
        type: TransactionType = TransactionType.CREDIT,
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

    # Do not compute counterparty it-self
    def _operate(self) -> TransactionResult:
        msg:str = f"{self.__class__.__name__} Operate:"

        try:
            self._operand.deposit(self.amount)  # Se Não lançar uma Exceção

            self._status = TransactionStatus.COMPLETED
            msg += f"{self._type.value} realizado com sucesso"

        except Exception as e:
            self._status = TransactionStatus.FAILED
            msg += f"{self._type.value} falhou: {str(e)}"

        return self._build_result(self._status, msg) # Corrigido para passar self._status (enum)

    # # Em que caso seria executado
    # def _revert(self) -> TransactionResult:
    #     msg: str = f"{self.__class__.__name__} Revert:"
    #
    #     try:
    #         self._operand.withdraw(self.amount)  # Se Não lançar uma Exceção
    #
    #         self._status = True
    #         msg += f"Restorno de {self._type.value} realizado com sucesso"
    #
    #     except Exception as e:
    #         self._status = False
    #         msg += f"Restorno de {self._type.value} falhou: {str(e)}"
    #
    #     return self._build_result(self._status, msg)