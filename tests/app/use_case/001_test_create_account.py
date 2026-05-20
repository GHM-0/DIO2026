from decimal import Decimal
import pytest
from application.dto.account_dto import CreateAccountRequest, AccountResponse
from application.use_case.account.create_account import CreateAccount
from infrastructure.persistence.repository.account_repository_impl import AccountRepository



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
