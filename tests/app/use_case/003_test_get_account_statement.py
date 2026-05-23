from decimal import Decimal

import pytest

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

    transference_saved1 = await create_transaction_use_case.execute(transference_request,requester_user_id=111)
    transference_saved2 = await create_transaction_use_case.execute(transference_request, requester_user_id=111)

    # Act
    # Adicionado limit e skip como None
    account_statement = await get_account_statement_use_case.execute(created_account1.id, limit=None, skip=None)

    # Assert
    assert isinstance(account_statement, AccountStatementResponse)
    assert account_statement.account.id == created_account1.id
    assert account_statement.account.user_id == created_account1.user_id
    assert account_statement.account.balance == created_account1.balance - amount - amount
    assert len(account_statement.transactions) == 2
    
    # Transações Associadas a conta
    transactions = [(t.amount, t.type) for t in account_statement.transactions]

    assert Decimal("20.00"), TransactionType.TRANSFERENCE in transactions


@pytest.mark.asyncio
async def test_deve_retornar_o_estado_atual_da_conta_pelo_id_sem_transacoes(uow: IAsyncDbTransactionUnit):
    # Arrange
    # Casos de Uso com UoW e Classes de Repositório
    create_account_use_case = CreateAccount(uow, AccountRepository)
    create_transaction_use_case = CreateTransaction(uow, TransactionRepository, AccountRepository)
    get_account_statement_use_case = GetAccountStatement(uow, AccountRepository, TransactionRepository)

    # Conta DTO
    account_request1 = CreateAccountRequest(user_id=4567, balance=Decimal('100.00'))


    created_account1 = await create_account_use_case.execute(account_request1)


    # Act
    # Adicionado limit e skip como None
    account_statement = await get_account_statement_use_case.execute(created_account1.id, limit=None, skip=None)

    # Assert
    assert isinstance(account_statement, AccountStatementResponse)
    assert account_statement.account.id == created_account1.id
    assert account_statement.account.user_id == created_account1.user_id
    assert account_statement.account.balance == Decimal("100.00")
    assert len(account_statement.transactions) == 0


@pytest.mark.asyncio
async def test_deve_retornar_erro_quando_conta_nao_existir(uow: IAsyncDbTransactionUnit):
    # Arrange
    get_account_statement_use_case = GetAccountStatement(uow, AccountRepository, TransactionRepository)

    id_inexistente = 99999

    # Act & Assert
    with pytest.raises(ValueError) as e:
        await get_account_statement_use_case.execute(id_inexistente, limit=None, skip=None)
    assert f"Conta com ID {id_inexistente} não encontrada." in str(e.value)

# Casos Ainda Não Cobertos (e por que são importantes para GetAccountStatement):
# •
# Conta como Destino de Transferências:
# ◦
# Nenhum dos testes atuais verifica o extrato de uma conta que recebeu transferências. O test_deve_retornar_o_estado_atual_da_conta_pelo_id verifica apenas a conta que enviou. Para o GetAccountStatement, é fundamental garantir que as transações de entrada sejam corretamente registradas e que o saldo seja atualizado.
# ◦
# Exemplo: No test_deve_retornar_o_estado_atual_da_conta_pelo_id, a created_account2 recebeu duas transferências de 50.00. Seu saldo final deveria ser 200.00 e seu extrato deveria mostrar duas transações de entrada. Este cenário não é testado.
# •
# Conta com Múltiplas Transferências (Origem e Destino):
# ◦
# Nenhum teste verifica uma conta que tanto enviou quanto recebeu transferências. Isso é crucial para garantir que o extrato consolide corretamente ambos os tipos de transação e que o saldo final seja o resultado líquido.