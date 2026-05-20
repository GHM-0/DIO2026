from decimal import Decimal

import pytest

from application.use_case.account.get_account_by_id import GetAccountByID
from application.dto.account_dto import AccountResponse
from infrastructure.persistence.repository.account_repository_impl import AccountRepository

@pytest.mark.asyncio
async def test_deve_retornar_uma_conta_valida_por_id(uow, create_account):
    """Deve recuperar uma conta existente usando o use case GetAccountByID."""

    # Arrange
    account_created = await create_account(user_id=10, balance=Decimal("1500.00"))
    
    # O Use Case espera (uow, repo_class) conforme definido na implementação
    use_case = GetAccountByID(uow, AccountRepository)

    # Act
    result = await use_case.execute(account_created.id)

    # Assert
    assert isinstance(result, AccountResponse)
    assert result.id == account_created.id
    assert result.user_id == 10
    assert result.balance == Decimal("1500.00")

@pytest.mark.asyncio
async def test_deve_retornar_none_quando_conta_nao_existir(uow):
    """Deve retornar None quando o ID da conta não for encontrado."""

    # Arrange
    use_case = GetAccountByID(uow, AccountRepository)
    id_inexistente = 99999

    # Act
    result = await use_case.execute(id_inexistente)

    # Assert
    assert result is None
