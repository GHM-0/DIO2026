from decimal import Decimal
import pytest
import pytest_asyncio

# Importações necessárias para o use case e DTOs
from application.dto.account_dto import CreateAccountRequest
from application.dto.transaction_dto import CreateTransactionRequest, TransactionResponse

from application.use_case.account.create_account import CreateAccount
from application.use_case.account.get_account_by_id import GetAccountByID

from exception.application.use_case.exception.create_transaction_exception import TransactionNaoPodeSerCriadoException

from application.use_case.transaction.create_transaction import CreateTransaction

from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType

from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from infrastructure.persistence.repository.transaction_repository_impl import TransactionRepository

@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database(truncate_table):
    """Garante que as tabelas de contas e transações estejam vazias para cada teste."""
    await truncate_table("transactions")
    await truncate_table("accounts")

@pytest.mark.asyncio
@pytest.mark.parametrize("conta_origem,conta_destino,valor,tipo,balance",[
    (111,222,Decimal("50.00"),TransactionType.TRANSFERENCE,Decimal('1000.00')),
    (234,7653,Decimal("345.78"),TransactionType.TRANSFERENCE,Decimal('1000.00'))
])
async def test_deve_criar_uma_transacao_de_transferencia_valida_entre_contas_distintas(uow,conta_origem,conta_destino,valor,tipo,balance):
    # Arrange
    # Criar a conta
    create_account_use_case = CreateAccount(uow, AccountRepository)

    # Obter o Estado Atual
    get_account_by_id_use_case = GetAccountByID(uow, AccountRepository)

    # Criar a Transação
    create_transaction_use_case = CreateTransaction(uow, TransactionRepository, AccountRepository)

    # Conta DTO
    account_request1 = CreateAccountRequest(user_id=conta_origem, balance=balance)
    account_request2 = CreateAccountRequest(user_id=conta_destino, balance=balance)

    # Contas criadas
    created_account1 = await create_account_use_case.execute(account_request1)
    created_account2 = await create_account_use_case.execute(account_request2)

    # Transações DTOs
    transference_request = CreateTransactionRequest(
        account_orig_id=created_account1.id,
        account_dest_id=created_account2.id,
        amount=valor,
        type=tipo
    )

    # Criação da Transação
    transference_saved1 = await create_transaction_use_case.execute(transference_request, requester_user_id=created_account1.user_id)

    saved_account1 = await get_account_by_id_use_case.execute(created_account1.id)
    saved_account2 = await get_account_by_id_use_case.execute(created_account2.id)

    # Assert detalhes em Transação
    assert isinstance(transference_saved1, TransactionResponse)
    assert transference_saved1.account_orig_id == created_account1.id
    assert transference_saved1.account_dest_id == created_account2.id
    assert transference_saved1.amount == valor
    assert transference_saved1.type == tipo
    assert transference_saved1.status == TransactionStatus.COMPLETED

    # Assert estado atual das contas
    assert saved_account1.balance == balance - valor
    assert saved_account2.balance == balance + valor

@pytest.mark.asyncio
@pytest.mark.parametrize("conta_origem,conta_destino,valor,tipo,balance",[
    (100,7652,Decimal("150.00"),TransactionType.TRANSFERENCE,Decimal('100.00')),
    (200,7653,Decimal("345.78"),TransactionType.TRANSFERENCE,Decimal('100.00'))
])
async def test_nao_deve_criar_transacao_com_saldo_insuficiente_na_conta_origem(uow,conta_origem,conta_destino,valor,tipo,balance):

        # Arrange
        # Criar a conta
        create_account_use_case = CreateAccount(uow, AccountRepository)

        # Obter o Estado Atual
        get_account_by_id_use_case = GetAccountByID(uow, AccountRepository)

        # Criar a Transação
        create_transaction_use_case = CreateTransaction(uow, TransactionRepository, AccountRepository)

        # Conta DTO
        account_request1 = CreateAccountRequest(user_id=conta_origem, balance=balance)
        account_request2 = CreateAccountRequest(user_id=conta_destino, balance=balance)

        # Contas criadas
        created_account1 = await create_account_use_case.execute(account_request1)
        created_account2 = await create_account_use_case.execute(account_request2)

        # Transações DTOs
        transference_request = CreateTransactionRequest(
            account_orig_id=created_account1.id,
            account_dest_id=created_account2.id,
            amount=valor,
            type=tipo
        )

        with pytest.raises(TransactionNaoPodeSerCriadoException) as e:
            await create_transaction_use_case.execute(transference_request,
                                                      requester_user_id=created_account1.user_id)
        assert "saldo insuficiente para saque" in str(e.value)

        # As contas não devem ser alteradas
        saved_account1 = await get_account_by_id_use_case.execute(created_account1.id)
        saved_account2 = await get_account_by_id_use_case.execute(created_account2.id)

        assert saved_account1.balance == balance
        assert saved_account2.balance == balance


# Barrado pelo DTO
# test_nao_deve_criar_transacao_com_conta_origem_ou_destino_inexistente(uow,conta_origem,conta_destino,valor,tipo,balance):
# test_nao_deve_criar_transacao_com_conta_destino_inexistente(uow,conta_origem,conta_destino,valor,tipo,balance):
# test_nao_deve_criar_transacao_com_valor_negativo(uow,conta_origem,conta_destino,valor,tipo,balance):
# test_nao_deve_criar_transacao_com_valor_zero(uow,conta_origem,conta_destino,valor,tipo,balance):

@pytest.mark.asyncio
@pytest.mark.parametrize("conta_origem,conta_destino,valor,tipo,balance",[
    (111,111,Decimal("50.00"),TransactionType.TRANSFERENCE,Decimal('1000.00')),
    (234,234,Decimal("345.78"),TransactionType.TRANSFERENCE,Decimal('1000.00'))
])
async def test_nao_deve_criar_transacao_entre_a_mesma_conta_origem_e_destino(uow,conta_origem,conta_destino,valor,tipo,balance):
    # Arrange
    # Criar a conta
    create_account_use_case = CreateAccount(uow, AccountRepository)

    # Obter o Estado Atual
    get_account_by_id_use_case = GetAccountByID(uow, AccountRepository)

    # Criar a Transação
    create_transaction_use_case = CreateTransaction(uow, TransactionRepository, AccountRepository)

    # Conta DTO
    account_request1 = CreateAccountRequest(user_id=conta_origem, balance=balance)
    account_request2 = CreateAccountRequest(user_id=conta_destino, balance=balance)

    # Contas criadas
    created_account1 = await create_account_use_case.execute(account_request1)
    created_account2 = await create_account_use_case.execute(account_request2)

    # Transações DTOs
    transference_request = CreateTransactionRequest(
        account_orig_id=created_account1.id,
        account_dest_id=created_account1.id,
        amount=valor,
        type=tipo
    )

    transference_saved1 = None
    # Criação da Transação
    with pytest.raises(TransactionNaoPodeSerCriadoException) as e:
        transference_saved1 = await create_transaction_use_case.execute(transference_request,
                                                                        requester_user_id=created_account1.user_id)
    assert f"Erro ao Criar Transação:Não é possível operar Transference entre a mesma conta {created_account1.id}" in str(e.value)

    saved_account1 = await get_account_by_id_use_case.execute(created_account1.id)
    saved_account2 = await get_account_by_id_use_case.execute(created_account2.id)

    # Assert detalhes em Transação
    assert transference_saved1 is None

    # Assert estado atual das contas
    assert saved_account1.balance == balance
    assert saved_account2.balance == balance