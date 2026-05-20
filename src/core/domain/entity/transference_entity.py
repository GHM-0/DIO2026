# src.core.domain.entity.transaction.transference_entity.py
from datetime import datetime
from decimal import Decimal
from core.domain.entity.account_entity import Account
from core.domain.entity.transaction_entity import Transaction
from core.domain.entity.credit_entity import Credit
from core.domain.entity.debit_entity import Debit
from core.domain.value_object.transaction_result import TransactionResult
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
        self._operate()

    def _operate(self) -> TransactionResult:
        """
        Executa a transferência orquestrando as operações unárias.
        """

        try:
            debit = Debit(operand=self._operand, counterparty=self._destination, amount=self.amount)

            if debit._status:
                credit = Credit(operand=self._operand, counterparty=self._destination, amount=self.amount)

                if credit._status:
                    self._status=True
                    return self._build_result(self._status, f"{self.__class__.__name__} realizada com sucesso")

        except Exception as e:
            self._status = False
            return self._build_result(self._status, f"{self.__class__.__name__}  falhou:{e}")



    def _reverse(self) -> TransactionResult:
        """
        Reverte a transferência via operações unárias opostas.
        """

        return self._build_result(self._status, f"{self.__class__.__name__} Revertida")