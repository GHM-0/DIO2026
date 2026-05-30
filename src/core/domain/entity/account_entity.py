# src.core.domain.entity.account_entity.py

from datetime import datetime
from decimal import Decimal

from exception.core.exception.entity.account.account_exception import (
    InsufficientBalance,
    InvalidUser,
    InvalidId,
)

from core.domain.value_object.amount import Amount
from core.domain.value_object.balance import Balance
from exception.core.exception.value_object.balance_exception import InvalidBalance


class Account:
    """
    Entidade de Conta: Implementa validação distribuída por etapa do ciclo de vida.
    Garante que nenhum objeto exista em estado transitório inválido.
    """

    _id: int | None
    _user_id: int
    _balance: Decimal
    _created_at: datetime | None

    def __init__(self, *, account_id: int|None = None, user_id: int, balance: Decimal, created_at: datetime | None = None) -> None:
        self._id = account_id
        self._user_id = user_id

        self._balance = Balance.validate(balance)
        self._created_at = created_at

        self.__post_init__()

    def __post_init__(self) -> None:
        if self._user_id <= 0:
            raise InvalidUser("Usuário não encontrado")

        if not isinstance(self._balance, Decimal):
            raise InvalidBalance("saldo inválido para conta")

        if self._id is not None and self._id <= 0:
            raise InvalidId("ID inválido na criação da conta")

    @property
    def user_id(self) -> int: return self._user_id

    @property
    def balance(self) -> Decimal: return self._balance

    @property
    def created_at(self) -> datetime | None:
        return self._created_at

    @property
    def id(self) -> int | None:
        return self._id

    # Operações Internas
    def deposit(self, amount: Decimal) -> None:
        Amount.validate(amount)
        self._balance += amount

    def withdraw(self, amount: Decimal) -> None:
        Amount.validate(amount)

        if amount > self._balance:
            raise InsufficientBalance("saldo insuficiente para saque")

        self._balance -= amount


    def is_persisted(self) -> bool:
        return (self.id is not None) and (self.created_at is not None) and self.id > 0

    def __eq__(self, other:object) -> bool:
        if not isinstance(other, Account):
            return False

        return self.id == other.id

    # Formato clássico construtor
    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"transaction_id={self.id!r}, "
            f"user_id={self.user_id!r}, "
            f"balance={self.balance!r}, "
            f"created_at={self.created_at}"   #datetime has no "!r" repr
            f")"
        )

    # Formato Linha
    def __str__(self) -> str:
        return f"Conta {self.id} (Usuário: {self.user_id}) - saldo: R${self.balance:,.2f}, criada em:{self.created_at}"