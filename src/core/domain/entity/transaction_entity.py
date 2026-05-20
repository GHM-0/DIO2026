# src.core.domain.entity.transaction_entity.py
from abc import abstractmethod, ABC
from datetime import datetime
from decimal import Decimal

from core.domain.entity.account_entity import Account
from core.domain.value_object.transaction_result import TransactionResult
from core.exception.entity.transaction.transaction_exception import (
    InvalidAccount,
    InvalidId, SameAccountException,
)

from core.domain.value_object.amount import Amount
from core.domain.value_object.transaction_type import TransactionType

class Transaction(ABC):
    """
    Representa uma transação financeira abstrata entre duas contas.
    """
    _status: bool| None

    _id: int | None
    _operand: Account
    _counterparty: Account
    _type: TransactionType
    _amount: Decimal
    _timestamp: datetime | None

    def __init__(
        self,
        *,
        id: int | None = None,
        operand: Account,
        counterparty: Account| None = None,
        type: TransactionType,
        amount: Decimal,
        timestamp: datetime | None = None
    ) -> None:
        self._id = id
        self._operand = operand
        self._destination = counterparty
        self._type = type
        self._amount = Amount.validate(amount)
        self._timestamp = timestamp
        self._status = None

        self.__post_init__()
        self._operate()


    def __post_init__(self):

        if self._operand.id is not None and self._operand.id <= 0:
            raise InvalidAccount(f"{self._operand.__class__.__name__} Origem não encontrada")

        if self._destination.id is not None and self._destination.id <= 0:
            raise InvalidAccount(f"{self._destination.__class__.__name__} Destino não encontrada")

        if self._id is not None and self._id <= 0:
            raise InvalidId(f"ID inválido na criação da {self.__class__.__name__}")

    @property
    def account_orig_id(self) -> int | None:
        return self._operand.id

    @property
    def account_dest_id(self) -> int | None:
        return self._destination.id

    @property
    def amount(self) -> Decimal: return self._amount

    @property
    def type(self) -> TransactionType: return self._type

    @property
    def id(self) -> int | None: return self._id

    @property
    def timestamp(self) -> datetime | None: return self._timestamp

    @property
    def status(self) -> str:
        return "Concluded" \
            if self._status is True \
            else "Reverted" \
            if self._status is False \
            else "Pending"

    @abstractmethod
    def _operate(self) -> TransactionResult:
        ...

    def _build_result(self, success: bool, message: str) -> TransactionResult:
        """Constrói um objeto TransactionResult com os dados atuais da transação."""
        return TransactionResult(
            success=success,
            message=message,
            transaction_id=self.id,
            transaction_type=self.type,
            amount=self.amount,
            origin_id=self.account_orig_id,
            destination_id=self.account_dest_id,
            timestamp=self.timestamp or datetime.now()
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, Transaction): return False
        return self.id == other.id

    def __repr__(self) -> str:
        return (
            f"{self.status}:{self.__class__.__name__}"
            f"(id={self.id!r}, "
            f"type={self.type.value}, "
            f"origin={self.account_orig_id}, "
            f"destination={self.account_dest_id}, "
            f"amount={self.amount})"
        )