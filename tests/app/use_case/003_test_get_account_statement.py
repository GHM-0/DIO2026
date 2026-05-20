from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from application.use_case.account.create_account import CreateAccount
from application.use_case.transaction.create_transaction import CreateTransaction
from application.use_case.get_account_statement import GetAccountStatement
from application.dto.account_statement_dto import AccountStatementResponse
from application.dto.account_dto import CreateAccountRequest
from application.dto.transaction_dto import CreateTransactionRequest
from core.domain.value_object.transaction_type import TransactionType

from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from infrastructure.persistence.repository.transaction_repository_impl import TransactionRepository
from core.domain.port.async_db_transaction_unit_interface import IAsyncDbTransactionUnit


@pytest.mark.asyncio
async def test_deve_retornar_o_estado_atual_da_conta_pelo_id(uow: IAsyncDbTransactionUnit):

    # Arrange
    # Casos de Uso com UoW e Classes de Repositório
    create_account_use_case = CreateAccount(uow, AccountRepository)
    create_transaction_use_case = CreateTransaction(uow, TransactionRepository,AccountRepository)
    get_account_statement_use_case = GetAccountStatement(uow, AccountRepository, TransactionRepository)

    # Conta DTO
    account_request = CreateAccountRequest(user_id=1, balance=Decimal('100.00'))
    created_account = await create_account_use_case.execute(account_request)

    # Transações DTOs
    deposit_request = CreateTransactionRequest(
        account_orig_id=created_account.id,
        account_dest_id=created_account.id,
        amount=Decimal('50.00'),
        type=TransactionType.CREDIT
    )
    await create_transaction_use_case.execute(deposit_request)

    withdraw_request = CreateTransactionRequest(
        account_orig_id=created_account.id,
        account_dest_id=None,
        amount=Decimal('20.00'),
        type=TransactionType.DEBIT
    )
    await create_transaction_use_case.execute(withdraw_request)

    # Act
    # Adicionado limit e skip como None
    account_statement = await get_account_statement_use_case.execute(created_account.id, limit=None, skip=None)

    # Assert
    assert isinstance(account_statement, AccountStatementResponse)
    assert account_statement.account.id == created_account.id
    assert account_statement.account.user_id == created_account.user_id
    assert account_statement.account.balance == created_account.balance
    assert len(account_statement.transactions) == 2
    
    # Transações Associadas a conta
    transactions = [(t.amount, t.type) for t in account_statement.transactions]

    assert (Decimal("20.00"), TransactionType.DEBIT) in transactions
    assert (Decimal("50.00"), TransactionType.CREDIT) in transactions

@pytest.mark.asyncio
async def test_deve_retornar_erro_quando_conta_nao_existir(uow: IAsyncDbTransactionUnit):
    # Arrange
    get_account_statement_use_case = GetAccountStatement(uow, AccountRepository, TransactionRepository)

    id_inexistente = 99999

    # Act & Assert
    with pytest.raises(ValueError) as e:
        await get_account_statement_use_case.execute(id_inexistente, limit=None, skip=None)
    assert f"Conta com ID {id_inexistente} não encontrada." in str(e.value)