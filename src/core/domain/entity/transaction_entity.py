# src.core.domain.entity.transaction_entity.py
from abc import abstractmethod, ABC
from datetime import datetime
from decimal import Decimal
from typing import Self

from core.domain.entity.account_entity import Account
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
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
    _status: TransactionStatus

    _id: int | None
    _account_orig_id: int
    _account_dest_id: int
    _transaction_type: TransactionType
    _amount: Decimal
    _timestamp: datetime | None

    def __init__(
        self,
        *,
        id: int | None = None,
        account_orig_id: int,
        account_dest_id: int,
        amount: Decimal,
        timestamp: datetime | None = None
    ) -> None:
        self._id = id
        self._account_orig_id = account_orig_id
        self._account_dest_id = account_dest_id
        self._amount = Amount.validate(amount)
        self._timestamp = timestamp
        self._status = TransactionStatus.CREATED

        self.__post_init__()

    @classmethod
    def create(
        cls,
        *,
        id: int | None = None,
        account_orig: Account,
        account_dest: Account,
        amount: Decimal,
        timestamp: datetime | None = None
    ) -> Self:
        instance = cls(
            id=id,

            account_orig_id=account_orig.id,
            account_dest_id=account_dest.id,

            amount=amount,
            timestamp=timestamp
        )
        instance._operate(account_orig=account_orig, account_dest=account_dest)
        return instance


    def __post_init__(self):
        # Validações agora usam os IDs diretamente
        if self._account_orig_id <= 0:
            raise InvalidAccount(f"ID da conta de origem inválido: {self._account_orig_id}")

        if self._account_dest_id <= 0:
            raise InvalidAccount(f"ID da conta de destino inválido: {self._account_dest_id}")

        if self._account_orig_id == self._account_dest_id:
            raise SameAccountException(f"Não é possível operar {self.__class__.__name__} entre a mesma conta {self._account_orig_id}")

        if self._id is not None and self._id <= 0:
            raise InvalidId(f"ID inválido na criação da {self.__class__.__name__}")

    @property
    def account_orig_id(self) -> int | None:
        return self._account_orig_id

    @property
    def account_dest_id(self) -> int | None:
        return self._account_dest_id

    @property
    def amount(self) -> Decimal: return self._amount

    @property
    def type(self) -> TransactionType: return self._transaction_type

    @property
    def id(self) -> int | None: return self._id

    @property
    def timestamp(self) -> datetime | None: return self._timestamp

    @property
    def status(self) -> str:
        return  self._status.value

    @abstractmethod
    def _operate(self, account_orig: Account, account_dest: Account) -> TransactionResult: # Assinatura atualizada
        ...

    def _build_result(self, status: str, message: str) -> TransactionResult:
        """Constrói um objeto TransactionResult com os dados atuais da transação."""
        return TransactionResult(
            status = status,
            message = message,
            transaction_id = self.id,
            transaction_type = self.type,
            amount = self.amount,
            account_orig_id = self.account_orig_id,
            account_dest_id = self.account_dest_id,
            timestamp = self.timestamp or datetime.now()
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