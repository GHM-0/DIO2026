# src.core.domain.entity.transaction_entity.py

from abc import abstractmethod, ABC
from datetime import datetime
from decimal import Decimal
from typing import Self

from core.domain.entity.account_entity import Account
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
from exception.core.exception.entity.transaction.transaction_exception import (
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

    _message:str = "Transação De tipo Inválido!"


    def __init__(
        self,
        *,
        transaction_id: int | None = None,
        account_orig_id: int,
        account_dest_id: int,
        #transaction_type: TransactionType,
        amount: Decimal,
        timestamp: datetime | None = None,
        status: TransactionStatus | None = None
    ) -> None:
        self._id = transaction_id
        self._account_orig_id = account_orig_id
        self._account_dest_id = account_dest_id
        #self._transaction_type = self.type
        self._amount = Amount.validate(amount)
        self._timestamp = timestamp
        self._status = status if status is not None else TransactionStatus.CREATED

        self.__post_init__()

    @classmethod
    def create(
        cls,
        *,
        transaction_id: int | None = None,
        account_orig: Account,
        account_dest: Account,
        amount: Decimal,
        timestamp: datetime | None = None
    ) -> Self:

        if account_orig is None or account_orig.id is None:
            raise InvalidAccount("A conta de origem não pode ser nula ou ter ID nulo.")

        if account_dest is None or account_dest.id is None:
            raise InvalidAccount("A conta de destino não pode ser nula ou ter ID nulo.")

        instance = cls(
            transaction_id = transaction_id,

            account_orig_id = account_orig.id,
            account_dest_id = account_dest.id,

            amount=amount,   #Amount.validate(amount) redundante
            timestamp=timestamp
        )
        instance._operate(account_orig=account_orig, account_dest=account_dest)
        return instance


    def __post_init__(self) -> None:
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
    def account_orig_id(self) -> int:
        return self._account_orig_id

    @property
    def account_dest_id(self) -> int:
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
    def status(self) -> TransactionStatus:
        return  self._status

    @property
    def message(self) -> str:
        return self._message

    @abstractmethod
    def _operate(self, account_orig: Account, account_dest: Account) -> TransactionResult: # Assinatura atualizada
        ...

    def _build_result(self) -> TransactionResult:
        """Constrói um objeto TransactionResult com os dados atuais da transação."""

        return TransactionResult(
            status = self.status,
            message = self.message,
            transaction_id = self.id,
            transaction_type = self.type,
            amount = self.amount,
            account_orig_id = self.account_orig_id,
            account_dest_id = self.account_dest_id,
            timestamp = self.timestamp or datetime.now(),
        )


    def is_persisted(self) -> bool:
        return (self.id is not None) and (self.timestamp is not None) and self.id > 0

    def __eq__(self, other:object) -> bool:
        if not isinstance(other, Transaction): return False
        return self.id == other.id

    def __repr__(self) -> str:
        return (
            f"{self.status}:{self.__class__.__name__}"
            f"(transaction_id={self.id!r}, "
            f"type={self.type.value}, "
            f"origin={self.account_orig_id}, "
            f"destination={self.account_dest_id}, "
            f"amount={self.amount})"
        )