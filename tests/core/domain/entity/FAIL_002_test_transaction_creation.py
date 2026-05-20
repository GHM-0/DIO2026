# tests/core/domain/entity/FAIL_002_test_transaction_creation.py
import datetime
from decimal import Decimal
import pytest

from core.exception.entity.transaction.transaction_exception import (
    InvalidAccount, 
    InvalidId
)
# Importamos a exceção correta lançada pelo Value Object Amount
from core.exception.value_object.amount_exception import InvalidAmount
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_type import TransactionType

# Testes De Criação
@pytest.mark.parametrize("account_id, type, amount", [(123, TransactionType.CREDIT, "10.00")])
def teste_deve_criar_uma_transacao_sem_id(account_id, type, amount):
    transaction = Transaction(
        id=None, 
        account_id=account_id, 
        type=type, 
        amount=Decimal(amount),
        timestamp=datetime.datetime.now()
    )

    assert transaction.account_id == account_id
    assert transaction.amount == Decimal(amount)

# Teste De Restauração
@pytest.mark.parametrize("id, account_id, type, amount", [(1, 123, TransactionType.CREDIT, "100.00")])
def teste_deve_restaurar_uma_transacao_com_id_valido(id, account_id, type, amount):
    transaction = Transaction(
        id=id, 
        account_id=account_id, 
        type=type, 
        amount=Decimal(amount),
        timestamp=datetime.datetime.now()
    )

    assert transaction.id == id
    assert transaction.account_id == account_id
    assert transaction.amount == Decimal(amount)


@pytest.mark.parametrize("account_id, type, amount", [(-1, TransactionType.CREDIT, "10.00")])
def teste_deve_falhar_ao_criar_transacao_com_account_id_negativo(account_id, type, amount):
    with pytest.raises(InvalidAccount):
        Transaction(
            id=None, 
            account_id=account_id, 
            type=type, 
            amount=Decimal(amount),
            timestamp=datetime.datetime.now()
        )

@pytest.mark.parametrize("account_id, type, amount", [(123, TransactionType.DEBIT, "0.00")])
def teste_deve_falhar_ao_criar_transacao_com_valor_zero(account_id, type, amount):
    with pytest.raises(InvalidAmount):
        Transaction(
            id=None,
            account_id=account_id,
            type=type,
            amount=Decimal(amount),
            timestamp=datetime.datetime.now()
        )

@pytest.mark.parametrize("account_id, type, amount", [(123, TransactionType.CREDIT, "-50.00")])
def teste_deve_falhar_ao_criar_transacao_com_valor_negativo(account_id, type, amount):
    with pytest.raises(InvalidAmount):
        Transaction(
            id=None,
            account_id=account_id,
            type=type,
            amount=Decimal(amount),
            timestamp=datetime.datetime.now()
        )

@pytest.mark.parametrize("id, account_id, type, amount", [(-1, 123, TransactionType.CREDIT, "100.00")])
def teste_deve_falhar_ao_restaurar_transacao_com_id_negativo(id, account_id, type, amount):
    with pytest.raises(InvalidId):
        Transaction(
            id=id,
            account_id=account_id, 
            type=type, 
            amount=Decimal(amount),
            timestamp=datetime.datetime.now()
        )
