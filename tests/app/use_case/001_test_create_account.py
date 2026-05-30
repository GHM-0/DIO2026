from decimal import Decimal
import pytest
import pytest_asyncio

from application.dto.account_dto import CreateAccountRequest, AccountResponse
from application.use_case.account.create_account import CreateAccount
from infrastructure.persistence.repository.account_repository_impl import AccountRepository


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database(truncate_table):
    """Garante que as tabelas de contas e transações estejam vazias para cada teste."""
    await truncate_table("transactions")
    await truncate_table("accounts")


@pytest.mark.asyncio
async def test_deve_criar_uma_conta_valida(uow):
    # Arrange
    # Use Case espera (uow, repo_class)
    use_case = CreateAccount(uow, AccountRepository)

    request = CreateAccountRequest(user_id=1, balance=Decimal("100.00"))

    # Act
    result = await use_case.execute(request)

    # Assert
    assert isinstance(result, AccountResponse)
    assert result.user_id == 1
    assert result.balance == Decimal("100.00")

# Demais exceções são barradas pelo DTO

