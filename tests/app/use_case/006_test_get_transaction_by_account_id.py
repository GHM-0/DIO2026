from decimal import Decimal
import pytest

from application.dto.account_dto import CreateAccountRequest
from application.dto.account_statement_dto import AccountStatementResponse
from application.dto.transaction_dto import CreateTransactionRequest, TransactionResponse
from application.use_case.account.create_account import CreateAccount
from application.use_case.get_account_statement import GetAccountStatement
from application.use_case.transaction.create_transaction import CreateTransaction
from application.use_case.transaction.get_transaction_by_account_id import GetTransactionByAccountId
from application.use_case.transaction.get_transaction_by_id import GetTransactionById
from core.domain.value_object.transaction_type import TransactionType
from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from infrastructure.persistence.repository.transaction_repository_impl import TransactionRepository

@pytest.mark.asyncio
async def test_deve_retornar_transacoes_quando_conta_e_origem_ou_destino(uow):
    # Arrange
    # Casos de Uso com UoW e Classes de Repositório
    create_account_use_case = CreateAccount(uow, AccountRepository)
    create_transaction_use_case = CreateTransaction(uow, TransactionRepository, AccountRepository)
    get_account_statement_use_case = GetAccountStatement(uow, AccountRepository, TransactionRepository)

    get_transaction_by_id = GetTransactionById(uow, TransactionRepository)

    # Conta DTO
    account_request1 = CreateAccountRequest(user_id=111, balance=Decimal('100.00'))
    account_request2 = CreateAccountRequest(user_id=222, balance=Decimal('100.00'))

    created_account1 = await create_account_use_case.execute(account_request1)
    created_account2 = await create_account_use_case.execute(account_request2)

    amount = Decimal('50.00')

    # Transações DTOs
    transference_request = CreateTransactionRequest(
        account_orig_id=created_account1.id,
        account_dest_id=created_account2.id,
        amount=amount,
        type=TransactionType.TRANSFERENCE
    )

    transference_saved1 = await create_transaction_use_case.execute(transference_request, requester_user_id=111)
    transference_saved2 = await create_transaction_use_case.execute(transference_request, requester_user_id=111)

    # Act
    # Adicionado limit e skip como None
    account_statement1 = await get_account_statement_use_case.execute(created_account1.id, limit=None, skip=None)

    # Assert
    assert isinstance(account_statement1, AccountStatementResponse)
    assert account_statement1.account.id == created_account1.id
    assert account_statement1.account.user_id == created_account1.user_id
    assert account_statement1.account.balance == created_account1.balance - amount - amount
    assert len(account_statement1.transactions) == 2

    # Transações Associadas a conta origem
    transactions1_statement = [(t.amount, t.type) for t in account_statement1.transactions]
    assert transactions1_statement.count((Decimal("50.00"), TransactionType.TRANSFERENCE)) == 2

    account_statement2 = await get_account_statement_use_case.execute(created_account2.id, limit=None, skip=None)

    # Assert
    assert isinstance(account_statement2, AccountStatementResponse)
    assert account_statement2.account.id == created_account2.id
    assert account_statement2.account.user_id == created_account2.user_id
    assert account_statement2.account.balance == created_account2.balance + amount + amount
    assert len(account_statement2.transactions) == 2

    # Transações Associadas a conta destino
    transactions2_statement = [(t.amount, t.type) for t in account_statement2.transactions]
    assert transactions2_statement.count((Decimal("50.00"), TransactionType.TRANSFERENCE)) == 2

    recoverd_transaction1 = await get_transaction_by_id.execute(transference_saved1.id)
    recoverd_transaction2 = await get_transaction_by_id.execute(transference_saved2.id)

    # Assert
    assert isinstance(recoverd_transaction1, TransactionResponse)
    assert isinstance(recoverd_transaction2, TransactionResponse)

    get_transaction_by_account_id = GetTransactionByAccountId(uow, TransactionRepository)

    transactions1 = await get_transaction_by_account_id.execute(created_account1.id)
    transactions2 = await get_transaction_by_account_id.execute(created_account2.id)

    # Assertions for transactions retrieved by get_transaction_by_account_id
    assert isinstance(transactions1, list)
    assert len(transactions1) == 2
    for t in transactions1:
        assert isinstance(t, TransactionResponse)
        assert t.account_orig_id == created_account1.id
        assert t.account_dest_id == created_account2.id
        assert t.amount == amount
        assert t.type == TransactionType.TRANSFERENCE

    assert isinstance(transactions2, list)
    assert len(transactions2) == 2
    for t in transactions2:
        assert isinstance(t, TransactionResponse)
        assert t.account_orig_id == created_account1.id
        assert t.account_dest_id == created_account2.id
        assert t.amount == amount
        assert t.type == TransactionType.TRANSFERENCE

@pytest.mark.asyncio
async def test_deve_retornar_lista_vazia_quando_conta_nao_tem_transacoes(uow):
    # Arrange
    create_account_use_case = CreateAccount(uow, AccountRepository)
    account_request = CreateAccountRequest(user_id=333, balance=Decimal('0.00'))
    created_account = await create_account_use_case.execute(account_request)

    get_transaction_by_account_id = GetTransactionByAccountId(uow, TransactionRepository)

    # Act
    transactions = await get_transaction_by_account_id.execute(created_account.id)

    # Assert
    assert isinstance(transactions, list)
    assert len(transactions) == 0
    assert transactions == []

@pytest.mark.asyncio
@pytest.mark.parametrize("transaction_id",[None,0,-1])
async def test_deve_retornar_lista_vazia_quando_conta_nao_existir(uow,transaction_id):
    # Arrange
    get_transaction_by_account_id = GetTransactionByAccountId(uow, TransactionRepository)

    # Act
    transactions = await get_transaction_by_account_id.execute(transaction_id)

    # Assert
    assert isinstance(transactions, list)
    assert len(transactions) == 0
    assert transactions == []


@pytest.mark.asyncio
async def test_deve_retornar_transacoes_paginadas_corretamente(uow):
    # Arrange
    create_account_use_case = CreateAccount(uow, AccountRepository)
    create_transaction_use_case = CreateTransaction(uow, TransactionRepository, AccountRepository)

    account_request1 = CreateAccountRequest(user_id=111, balance=Decimal('1000.00'))
    account_request2 = CreateAccountRequest(user_id=222, balance=Decimal('1000.00'))

    created_account1 = await create_account_use_case.execute(account_request1)
    created_account2 = await create_account_use_case.execute(account_request2)

    amount = Decimal('10.00')
    num_transactions = 10
    expected_transactions = []

    # Criar várias transações para created_account1 como origem
    for i in range(num_transactions):
        transference_request = CreateTransactionRequest(
            account_orig_id=created_account1.id,
            account_dest_id=created_account2.id,
            amount=amount + i, # Variar o valor para facilitar a verificação da ordem
            type=TransactionType.TRANSFERENCE
        )
        saved_transaction = await create_transaction_use_case.execute(transference_request, requester_user_id=111)
        expected_transactions.append(saved_transaction)


    get_transaction_by_account_id = GetTransactionByAccountId(uow, TransactionRepository)

    # Act & Assert - Paginação
    # Teste 1: limit=5, skip=0
    transactions_page1 = await get_transaction_by_account_id.execute(created_account1.id, limit=5, skip=0)
    assert isinstance(transactions_page1, list)
    assert len(transactions_page1) == 5
    assert [t.id for t in transactions_page1] == [t.id for t in expected_transactions[0:5]]

    # Teste 2: limit=5, skip=5
    transactions_page2 = await get_transaction_by_account_id.execute(created_account1.id, limit=5, skip=5)
    assert isinstance(transactions_page2, list)
    assert len(transactions_page2) == 5
    assert [t.id for t in transactions_page2] == [t.id for t in expected_transactions[5:10]]

    # Teste 3: limit=3, skip=2
    transactions_page_custom = await get_transaction_by_account_id.execute(created_account1.id, limit=3, skip=2)
    assert isinstance(transactions_page_custom, list)
    assert len(transactions_page_custom) == 3
    assert [t.id for t in transactions_page_custom] == [t.id for t in expected_transactions[2:5]]

    # Teste 4: limit muito grande, skip=0 (deve retornar todas as transações restantes)
    transactions_all = await get_transaction_by_account_id.execute(created_account1.id, limit=20, skip=0)
    assert isinstance(transactions_all, list)
    assert len(transactions_all) == num_transactions
    assert [t.id for t in transactions_all] == [t.id for t in expected_transactions]

    # Teste 5: skip maior que o número total de transações (deve retornar lista vazia)
    transactions_empty_skip = await get_transaction_by_account_id.execute(created_account1.id, limit=5, skip=num_transactions)
    assert isinstance(transactions_empty_skip, list)
    assert len(transactions_empty_skip) == 0
    assert transactions_empty_skip == []

    # Teste 6: limit=None, skip=None (deve retornar todas as transações)
    transactions_no_limit_skip = await get_transaction_by_account_id.execute(created_account1.id, limit=None, skip=None)
    assert isinstance(transactions_no_limit_skip, list)
    assert len(transactions_no_limit_skip) == num_transactions
    assert [t.id for t in transactions_no_limit_skip] == [t.id for t in expected_transactions]