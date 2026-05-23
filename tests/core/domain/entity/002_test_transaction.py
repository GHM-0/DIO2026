# tests/core/domain/entity/002_test_transaction.py
import datetime

import pytest
from decimal import Decimal
from datetime import datetime

from core.domain.entity.account_entity import Account
from core.domain.entity.credit_entity import Credit
from core.domain.entity.debit_entity import Debit
from core.domain.entity.transaction_entity import Transaction
from core.domain.entity.transference_entity import Transference
from core.domain.value_object.transaction_result import TransactionResult
from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType
#from core.exception.entity.account.account_exception
from core.exception.entity.transaction.transaction_exception import SameAccountException, InvalidAccount, InvalidId
from core.exception.value_object.amount_exception import InvalidAmount

# Importar outras exceções e entidades conforme necessário

"""
Casos de Teste para a Entidade de Transação (Transferência)
Foco: Integridade de Domínio, Ordem de Execução e Lógica de Reversão
"""

# 1. TESTES DE INTEGRIDADE (VALIDAÇÃO PRÉ-OPERAÇÃO)
# -------------------------------------------------------------------------


def test_deve_lancar_excecao_ao_tentar_transferir_para_a_mesma_conta():
    """
    Objetivo: Garantir que account_orig e account_dest sejam obrigatoriamente distintas.
    Expectativa: SameAccountException.
    """

    account = Account(id=1,user_id=1,balance=Decimal("100"),created_at=datetime.now())

    with pytest.raises(SameAccountException) as e:
        Transference.create(account_orig=account, account_dest=account, amount=Decimal("10.00"))

    assert account.balance == Decimal(100.00)

    assert f"Não é possível operar Transference entre a mesma conta {account.id}" in str(e.value)

@pytest.mark.parametrize("orig,dest,amount",[
    (1,2,Decimal("-10.00")),
    (1,2,Decimal("0"))]
    )
def test_deve_lancar_excecao_se_valor_da_transacao_for_negativo_ou_zero(orig,dest,amount):
    """
    Objetivo: Garantir que o Amount Value Object barre valores inválidos.
    Expectativa: Erro de validação de Amount.
    """
    account1 = Account(id=orig,user_id=orig,balance=Decimal("100"),created_at=datetime.now())
    account2 = Account(id=dest, user_id=dest, balance=Decimal("100"), created_at=datetime.now())

    with pytest.raises(InvalidAmount) as e:
        Transference.create(account_orig=account1, account_dest=account2, amount=amount)

    assert "O valor deve ser positivo" in str(e)


# # 2. TESTES DE CAMINHO FELIZ (SUCESSO)
# # -------------------------------------------------------------------------


# Testa apenas o débito na conta origem
@pytest.mark.parametrize("orig,dest,balance_orig,balance_dest,amount",[
    (1,2,Decimal("100.00"),Decimal("100.00"),Decimal("10.00")),
    (3,4,Decimal("100.00"),Decimal("100.00"),Decimal("100"))]
    )
def test_deve_realizar_debito_com_sucesso_no_operand(orig,dest,balance_orig,balance_dest,amount):
    """
    Objetivo: Validar fluxo completo: débito na origem, crédito no destino.
    Expectativa: Status 'Concluded', saldos atualizados corretamente.
    """

    account1 = Account(id=orig,user_id=orig,balance=balance_orig,created_at=datetime.now())
    account2 = Account(id=dest, user_id=dest, balance=balance_dest, created_at=datetime.now())

    debit = Debit.create(id=orig,account_orig=account1,account_dest=account2,amount=amount,timestamp=datetime.now())

    # print(f"{debit}")

    assert debit.status == "Concluded"
    assert account1.balance == balance_orig - amount

# Testa apenas o crédito na conta origem
@pytest.mark.parametrize("orig,dest,balance_orig,balance_dest,amount",[
    (1,2,Decimal("100.00"),Decimal("100.00"),Decimal("10.00")),
    (3,4,Decimal("100.00"),Decimal("100.00"),Decimal("100"))]
    )
def test_deve_realizar_credito_com_sucesso_no_counterparty(orig,dest,balance_orig,balance_dest,amount):
    """
    Objetivo: Validar fluxo completo: débito na origem, crédito no destino.
    Expectativa: Status 'Concluded', saldos atualizados corretamente.
    """

    account1 = Account(id=orig,user_id=orig,balance=balance_orig,created_at=datetime.now())
    account2 = Account(id=dest, user_id=dest, balance=balance_dest, created_at=datetime.now())

    credit = Credit.create(id=orig,account_orig=account1,account_dest=account2,amount=amount,timestamp=datetime.now())

    # print(f"{credit}")

    assert credit.status == "Concluded"
    assert account2.balance == balance_dest + amount


# Simula uma transferência na conta origem
@pytest.mark.parametrize("orig,dest,balance_orig,balance_dest,amount",[
    (1,2,Decimal("100.00"),Decimal("100.00"),Decimal("10.00")),
    (3,4,Decimal("100.00"),Decimal("100.00"),Decimal("100"))]
    )
def test_deve_realizar_uma_transferencia_utilizando_credit_debit(orig,dest,balance_orig,balance_dest,amount):
    """
    Objetivo: Validar fluxo completo: débito na origem, crédito no destino.
    Expectativa: Status 'Concluded', saldos atualizados corretamente.
    """

    account1 = Account(id=orig,user_id=orig,balance=balance_orig,created_at=datetime.now())
    account2 = Account(id=dest, user_id=dest, balance=balance_dest, created_at=datetime.now())

    # print(f"\nInicial:{account1}\n{account2}")
    debit = Debit.create(id=orig, account_orig=account1, account_dest=account2, amount=amount, timestamp=datetime.now())
    credit = Credit.create(id=orig, account_orig=account1, account_dest=account2, amount=amount, timestamp=datetime.now())

    # print(f"{debit}")
    # print(f"{credit}")
    # print(f"\nFinal:{account1}\n{account2}")

    assert debit.status == "Concluded"
    assert account1.balance == balance_orig - amount
    assert credit.status == "Concluded"
    assert account2.balance == balance_dest + amount

# Utiliza transference para transferir quantias
@pytest.mark.parametrize("orig,dest,balance_orig,balance_dest,amount",[
    (1,2,Decimal("100.00"),Decimal("100.00"),Decimal("10.00")),
    # (3,4,Decimal("100.00"),Decimal("100.00"),Decimal("100"))
]
    )
def test_deve_realizar_uma_transferencia(orig,dest,balance_orig,balance_dest,amount):
    """
    Objetivo: Validar fluxo completo: débito na origem, crédito no destino.
    Expectativa: Status 'Concluded', saldos atualizados corretamente.
    """

    account1 = Account(id=orig,user_id=orig,balance=balance_orig,created_at=datetime.now())
    account2 = Account(id=dest, user_id=dest, balance=balance_dest, created_at=datetime.now())

    # print(f"Conta_origem, Saldo_inicial={account1.balance}")
    # print(f"Conta_destino, Saldo_destin={account2.balance}")

    transference = Transference.create(account_orig=account1,account_dest=account2,amount=amount)

    # print(f"{transference}")
    #
    # print(f"Conta_origem, Saldo_final={account1.balance}")
    # print(f"Conta_destino, Saldo_final={account2.balance}")

    assert transference.status == TransactionStatus.COMPLETED.value
    assert account1.balance == balance_orig - amount
    assert account2.balance == balance_dest + amount


@pytest.mark.parametrize("orig,dest,balance_orig,balance_dest,amount",[
    (1,2,Decimal("100.00"),Decimal("100.00"),Decimal("10.00")),
    (3,4,Decimal("100.00"),Decimal("100.00"),Decimal("100"))]
    )
def test_deve_retornar_transaction_result_correto_em_caso_de_sucesso(orig,dest,balance_orig,balance_dest,amount):
    """
    Objetivo: Validar se o objeto de resultado contém todos os dados da operação.
    Expectativa: success=True, IDs corretos, timestamp presente.
    """
    account1 = Account(id=orig,user_id=orig,balance=balance_orig,created_at=datetime.now())
    account2 = Account(id=dest, user_id=dest, balance=balance_dest, created_at=datetime.now())

    amount = Decimal("100.00")

    transference = Transference.create(account_orig=account1,account_dest=account2,amount=amount)

    assert transference is not None
    assert isinstance(transference,Transaction)
    assert transference.type == TransactionType.TRANSFERENCE
    assert transference.status == TransactionStatus.COMPLETED.value
    assert transference.amount == amount
    assert transference.account_orig_id == account1.id
    assert transference.account_dest_id == account2.id
    assert account1.balance == balance_orig - amount
    assert account2.balance == balance_dest + amount


    # print(f"{transference}")