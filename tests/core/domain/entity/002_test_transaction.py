# tests/core/domain/entity/002_test_transaction.py
import pytest
from decimal import Decimal

from core.domain.entity.account_entity import Account
from core.domain.entity.debit_entity import Debit
from core.domain.entity.transaction_entity import Transaction
from core.domain.entity.transference_entity import Transference
#from core.exception.entity.account.account_exception
from core.exception.entity.transaction.transaction_exception import SameAccountException
# Importar outras exceções e entidades conforme necessário

"""
Casos de Teste para a Entidade de Transação (Transferência)
Foco: Integridade de Domínio, Ordem de Execução e Lógica de Reversão
"""

# 1. TESTES DE INTEGRIDADE (VALIDAÇÃO PRÉ-OPERAÇÃO)
# -------------------------------------------------------------------------


def test_deve_lancar_excecao_ao_tentar_transferir_para_a_mesma_conta():
    """
    Objetivo: Garantir que operand e counterparty sejam obrigatoriamente distintas.
    Expectativa: SameAccountException.
    """

    account = Account(id=1,user_id=1,balance=Decimal("100"))

    print(f"\n{account}")

    with pytest.raises(SameAccountException) as e:
        transference = Transference(operand=account, counterparty=account, amount=Decimal("10.00"))


        print(f"\n{transference}")
        assert account.balance == Decimal(100.00)
        assert isinstance(transference,Transference)




# def test_deve_lancar_excecao_se_conta_origem_tiver_id_invalido():
#     """
#     Objetivo: Validar a integridade dos IDs das contas antes da operação.
#     Expectativa: InvalidAccount.
#     """
#     pass
#
# def test_deve_lancar_excecao_se_valor_da_transacao_for_negativo_ou_zero():
#     """
#     Objetivo: Garantir que o Amount Value Object barre valores inválidos.
#     Expectativa: Erro de validação de Amount.
#     """
#     pass
#
#
# # 2. TESTES DE CAMINHO FELIZ (SUCESSO)
# # -------------------------------------------------------------------------
#
# def test_deve_realizar_transferencia_com_sucesso_entre_duas_contas_validas():
#     """
#     Objetivo: Validar fluxo completo: débito na origem, crédito no destino.
#     Expectativa: Status 'Concluded', saldos atualizados corretamente.
#     """
#     pass
#
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
