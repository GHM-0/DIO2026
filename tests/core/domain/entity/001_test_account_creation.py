# tests/core/domain/entity/001_test_account_creation.py

from decimal import Decimal

import pytest

from exception.core.exception.value_object.balance_exception import (
    InvalidBalance)

from core.domain.entity.account_entity import Account

# Testes De Criação
@pytest.mark.parametrize("user_id,balance",[(1,"10.00")])
def teste_deve_criar_uma_conta(user_id,balance):

    account = Account(account_id=None,user_id=user_id,balance=Decimal(balance))

    assert account.user_id == user_id
    assert account.balance == Decimal(balance)

# Teste De Recriação
@pytest.mark.parametrize("transaction_id, user_id, balance",[(1,12,"0.023")])
def teste_deve_recriar_uma_conta(id,user_id,balance):
    account = Account(account_id=id,user_id=user_id,balance=Decimal(balance))

    assert account.id == id
    assert account.user_id == user_id
    assert account.balance == Decimal(balance)

@pytest.mark.parametrize("user_id, balance", [(1, "0.00")])
def teste_deve_falhar_ao_criar_conta_sem_saldo(user_id, balance):
    """Garante que a regra de negócio de saldo inicial positivo seja respeitada."""
    with pytest.raises(InvalidBalance):
        Account(account_id=None, user_id=user_id, balance=None)

# Violação de Acesso
def teste_deve_garantir_imutabilidade_do_id_e_user_id():
    """Valida que o transaction_id que imutável, conforme definido no design."""
    account = Account(account_id=1, user_id=1, balance=Decimal("100.00"))

    with pytest.raises(AttributeError):
        account.id = 2

    with pytest.raises(AttributeError):
        account.user_id = 2

def teste_deve_permitir_alteracao_do_saldo_via_atributo_privado():
    """Valida que o saldo é o único campo mutável, conforme definido no design."""
    account = Account(account_id=None, user_id=1, balance=Decimal("100.00"))

    account._balance = Decimal("200.00")
    assert account.balance == Decimal("200.00")
