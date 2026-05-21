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
from core.domain.value_object.transaction_status import TransactionStatus
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


# def test_deve_lancar_excecao_ao_tentar_transferir_para_a_mesma_conta():
#     """
#     Objetivo: Garantir que operand e counterparty sejam obrigatoriamente distintas.
#     Expectativa: SameAccountException.
#     """
#
#     account = Account(id=1,user_id=1,balance=Decimal("100"),created_at=datetime.now())
#
#     with pytest.raises(SameAccountException) as e:
#         Transference(operand=account, counterparty=account, amount=Decimal("10.00"))
#
#     assert account.balance == Decimal(100.00)
#
#     assert f"Não é possível operar Transference entre a mesma conta {account}" in str(e)
#
# # Coberto nos testes de Account
# # @pytest.mark.parametrize("orig,dest,amount",[
# #     (0,1,Decimal("10.00")),
# #     (1,0,Decimal("100.00"))]
# #     )
# # def test_deve_lancar_excecao_se_qualquer_uma_das_contas_tiver_id_invalido(orig,dest,amount):
# #     """
# #     Objetivo: Validar a integridade dos IDs das contas antes da operação.
# #     Expectativa: InvalidAccount.
# #     """
# #     pass
#
# @pytest.mark.parametrize("orig,dest,amount",[
#     (1,2,Decimal("-10.00")),
#     (1,2,Decimal("0"))]
#     )
# def test_deve_lancar_excecao_se_valor_da_transacao_for_negativo_ou_zero(orig,dest,amount):
#     """
#     Objetivo: Garantir que o Amount Value Object barre valores inválidos.
#     Expectativa: Erro de validação de Amount.
#     """
#     account1 = Account(id=orig,user_id=orig,balance=Decimal("100"),created_at=datetime.now())
#     account2 = Account(id=dest, user_id=dest, balance=Decimal("100"), created_at=datetime.now())
#
#     with pytest.raises(InvalidAmount) as e:
#         Transference(operand=account1, counterparty=account2, amount=amount)
#
#     assert "O valor deve ser positivo" in str(e)
#
#
# # # 2. TESTES DE CAMINHO FELIZ (SUCESSO)
# # # -------------------------------------------------------------------------
#
#
# # Testa apenas o debito na conta origem
# @pytest.mark.parametrize("orig,dest,balance_orig,balance_dest,amount",[
#     (1,2,Decimal("100.00"),Decimal("100.00"),Decimal("10.00")),
#     (3,4,Decimal("100.00"),Decimal("100.00"),Decimal("100"))]
#     )
# def test_deve_realizar_debito_com_sucesso_no_operand(orig,dest,balance_orig,balance_dest,amount):
#     """
#     Objetivo: Validar fluxo completo: débito na origem, crédito no destino.
#     Expectativa: Status 'Concluded', saldos atualizados corretamente.
#     """
#
#     account1 = Account(id=orig,user_id=orig,balance=balance_orig,created_at=datetime.now())
#     account2 = Account(id=dest, user_id=dest, balance=balance_dest, created_at=datetime.now())
#
#     debit = Debit(id=orig,operand=account1,counterparty=account2,amount=amount,timestamp=datetime.now())
#
#     print(f"{debit.status}")
#
#     assert debit.status == "Concluded"
#     assert account1.balance == balance_orig - amount
#
# # Testa apenas o credito na conta origem
# @pytest.mark.parametrize("orig,dest,balance_orig,balance_dest,amount",[
#     (1,2,Decimal("100.00"),Decimal("100.00"),Decimal("10.00")),
#     (3,4,Decimal("100.00"),Decimal("100.00"),Decimal("100"))]
#     )
# def test_deve_realizar_credito_com_sucesso_no_counterparty(orig,dest,balance_orig,balance_dest,amount):
#     """
#     Objetivo: Validar fluxo completo: débito na origem, crédito no destino.
#     Expectativa: Status 'Concluded', saldos atualizados corretamente.
#     """
#
#     account1 = Account(id=orig,user_id=orig,balance=balance_orig,created_at=datetime.now())
#     account2 = Account(id=dest, user_id=dest, balance=balance_dest, created_at=datetime.now())
#
#     credit = Credit(id=orig,operand=account1,counterparty=account2,amount=amount,timestamp=datetime.now())
#
#     print(f"{credit.status}")
#
#     assert credit.status == "Concluded"
#     assert account1.balance == balance_dest + amount
#
#
# # Simula uma transferência na conta origem
# @pytest.mark.parametrize("orig,dest,balance_orig,balance_dest,amount",[
#     (1,2,Decimal("100.00"),Decimal("100.00"),Decimal("10.00")),
#     (3,4,Decimal("100.00"),Decimal("100.00"),Decimal("100"))]
#     )
# def test_deve_realizar_uma_transferencia_utilizando_credit_debit(orig,dest,balance_orig,balance_dest,amount):
#     """
#     Objetivo: Validar fluxo completo: débito na origem, crédito no destino.
#     Expectativa: Status 'Concluded', saldos atualizados corretamente.
#     """
#
#     account1 = Account(id=orig,user_id=orig,balance=balance_orig,created_at=datetime.now())
#     account2 = Account(id=dest, user_id=dest, balance=balance_dest, created_at=datetime.now())
#
#     debit = Debit(id=orig, operand=account1, counterparty=account2, amount=amount, timestamp=datetime.now())
#     credit = Credit(id=orig,operand=account2,counterparty=account1,amount=amount,timestamp=datetime.now())
#
#     print(f"{debit.status}")
#     print(f"{credit.status}")
#
#     assert debit.status == "Concluded"
#     assert account1.balance == balance_orig - amount
#     assert credit.status == "Concluded"
#     assert account2.balance == balance_dest + amount
# Acima funciona

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

    print(f"Conta_origem, Saldo_inicial={account1.balance}")
    print(f"Conta_destino, Saldo_destin={account2.balance}")

    transference = Transference(operand=account1,counterparty=account2,amount=amount)

    print(f"{transference}")

    print(f"Conta_origem, Saldo_final={account1.balance}")
    print(f"Conta_destino, Saldo_final={account2.balance}")
    #
    # assert transference.status == TransactionStatus.COMPLETED.value
    # assert account1.balance == balance_orig - amount
    #
    # assert account2.balance == balance_dest + amount





# def test_deve_retornar_transaction_result_correto_em_caso_de_sucesso():
#     """
#     Objetivo: Validar se o objeto de resultado contém todos os dados da operação.
#     Expectativa: success=True, IDs corretos, timestamp presente.
#     """
#     pass
#
#
# # 3. TESTES DE FALHA DE DOMÍNIO (REGRAS DE NEGÓCIO)
# # -------------------------------------------------------------------------
#
# def test_deve_marcar_como_revertido_se_origem_nao_tiver_saldo_suficiente():
#     """
#     Objetivo: Validar que a transação não ocorre se o primeiro passo (withdraw) falhar.
#     Expectativa: Status 'Reverted', saldo do destino intacto, saldo da origem intacto.
#     """
#     pass
#
#
# # 4. TESTES DE CONSISTÊNCIA E REVERSÃO (CASOS COMPLEXOS)
# # -------------------------------------------------------------------------
#
# def test_deve_estornar_debito_na_origem_se_deposito_no_destino_falhar():
#     """
#     Objetivo: Validar a atomicidade do domínio (rollback manual).
#     Fluxo: Withdraw funciona -> Deposit falha -> Origin.deposit() deve ser chamado.
#     Expectativa: Status 'Reverted', saldo da origem volta ao valor original.
#     """
#     pass
#
# def test_nao_deve_executar_reversao_se_o_debito_inicial_sequer_ocorreu():
#     """
#     Objetivo: Garantir coerência na reversão (não estornar o que não saiu).
#     Expectativa: Status 'Reverted', nenhuma chamada de depósito compensatório.
#     """
#     pass
#
# def test_status_deve_ser_pending_durante_a_instanciacao_se_interrompido():
#     """
#     Objetivo: Validar o preciosismo do estado None/Pending inicial.
#     Expectativa: _status ser None até a conclusão do _operate.
#     """
#     pass