from decimal import Decimal
import pytest
import pytest_asyncio

from application.dto.account_dto import CreateAccountRequest
from application.dto.account_statement_dto import AccountStatementResponse
from application.dto.transaction_dto import CreateTransactionRequest, TransactionResponse
from application.use_case.account.create_account import CreateAccount
from application.use_case.get_account_statement import GetAccountStatement
from application.use_case.transaction.create_transaction import CreateTransaction
from application.use_case.transaction.get_transaction_by_id import GetTransactionById
from core.domain.value_object.transaction_type import TransactionType
from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from infrastructure.persistence.repository.transaction_repository_impl import TransactionRepository

@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database(truncate_table):
    """Garante que as tabelas de contas e transações estejam vazias para cada teste."""
    await truncate_table("transactions")
    await truncate_table("accounts")

@pytest.mark.asyncio
async def test_deve_retornar_uma_transacao_valida_por_id(uow):
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
    transactions1 = [(t.amount, t.type) for t in account_statement1.transactions]
    assert transactions1.count((Decimal("50.00"), TransactionType.TRANSFERENCE)) == 2

    account_statement2 = await get_account_statement_use_case.execute(created_account2.id, limit=None, skip=None)

    # Assert
    assert isinstance(account_statement2, AccountStatementResponse)
    assert account_statement2.account.id == created_account2.id
    assert account_statement2.account.user_id == created_account2.user_id
    assert account_statement2.account.balance == created_account2.balance + amount + amount
    assert len(account_statement2.transactions) == 2

    # Transações Associadas a conta destino
    transactions2 = [(t.amount, t.type) for t in account_statement2.transactions]
    assert transactions2.count((Decimal("50.00"), TransactionType.TRANSFERENCE)) == 2

    recoverd_transaction1 = await get_transaction_by_id.execute(transference_saved1.id)
    recoverd_transaction2 = await get_transaction_by_id.execute(transference_saved2.id)

    # Assert
    assert isinstance(recoverd_transaction1, TransactionResponse)
    assert isinstance(recoverd_transaction2, TransactionResponse)


@pytest.mark.asyncio
@pytest.mark.parametrize("transaction_id",[
    999,888,0,-99,None
])
async def test_deve_retornar_none_quando_transacao_nao_existir(uow,transaction_id):

    get_transaction_by_id = GetTransactionById(uow, TransactionRepository)

    recoverd_transaction1 = await get_transaction_by_id.execute(transaction_id)

    # Assert
    assert recoverd_transaction1 is None
