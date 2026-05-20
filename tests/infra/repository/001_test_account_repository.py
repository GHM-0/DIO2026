# tests/infra/repository/001_test_account_repository.py
from datetime import datetime

import pytest
import pytest_asyncio
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.account_dto import CreateAccountRequest
from core.domain.entity.account_entity import Account
from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from infrastructure.exception.persistence.persistence_exception import PersistenceException

@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database(truncate_table):
    """Garante que as tabelas de contas e transações estejam vazias para cada teste."""
    await truncate_table("transactions")
    await truncate_table("accounts")

@pytest.mark.asyncio
async def test_deve_criar_uma_conta_valida(db_session: AsyncSession):
    # Arrange
    repository = AccountRepository(db_session)
    account_dto = CreateAccountRequest(user_id=999, balance=Decimal("500.75"))
    account_entity = Account(user_id=account_dto.user_id, balance=account_dto.balance)

    # Act
    account_saved = await repository.save_one(account_entity)

    # Assert
    assert isinstance(account_saved, Account)
    assert account_saved.user_id == account_entity.user_id
    assert account_saved.balance == account_entity.balance

    # Check
    account_persisted = await repository.read_one(account_saved.id)
    assert account_persisted is not None
    assert account_persisted.id == account_saved.id

@pytest.mark.asyncio
async def test_deve_confirmar_existencia_de_conta_por_id(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    account_saved = await repository.save_one(Account(user_id=1, balance=Decimal("10.00")))
    assert await repository.exists_by_id(account_saved.id) is True

@pytest.mark.asyncio
async def test_deve_retornar_falso_quando_conta_nao_existe(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    assert await repository.exists_by_id(99999) is False

@pytest.mark.asyncio
async def test_deve_buscar_uma_conta_pelo_id(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    account_saved = await repository.save_one(Account(user_id=2, balance=Decimal("20.00")))
    account_persisted = await repository.read_one(account_saved.id)
    assert account_persisted is not None
    assert account_persisted.id == account_saved.id

@pytest.mark.asyncio
async def test_deve_atualizar_dados_da_conta(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    account_saved = await repository.save_one(Account(user_id=3, balance=Decimal("30.00")))
    account_saved.deposit(Decimal("70.00"))
    account_updated = await repository.update_one(account_saved)
    assert account_updated.balance == Decimal("100.00")

@pytest.mark.asyncio
async def test_deve_atualizar_dados_da_conta_saldo_negativo(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    account_saved = await repository.save_one(Account(user_id=3, balance=Decimal("-130.00")))
    assert account_saved.balance == Decimal("-130.00")

@pytest.mark.asyncio
async def test_deve_remover_uma_conta(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    account_saved = await repository.save_one(Account(user_id=4, balance=Decimal("40.00")))
    assert await repository.remove_one(account_saved.id) is True
    assert await repository.read_one(account_saved.id) is None

@pytest.mark.asyncio
async def test_deve_listar_todas_as_contas(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    await repository.save_one(Account(user_id=5, balance=Decimal("50.00")))
    await repository.save_one(Account(user_id=6, balance=Decimal("60.00")))
    accounts = await repository.read_all()
    assert len(accounts) >= 2

@pytest.mark.asyncio
async def test_deve_retornar_falso_ao_remover_id_que_nao_existe(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    assert await repository.remove_one(99999) is False

@pytest.mark.asyncio
async def test_deve_listar_contas_por_user_id(db_session: AsyncSession):
    repository = AccountRepository(db_session)
    await repository.save_one(Account(user_id=42, balance=Decimal("170.00")))
    await repository.save_one(Account(user_id=42, balance=Decimal("30.00")))
    accounts = await repository.get_all_by_user_id(user_id=42)
    assert len(accounts) == 2

@pytest.mark.asyncio
async def test_deve_retornar_dados_inalterados_com_update_vazio(db_session):
    repository = AccountRepository(db_session)
    account_saved = await repository.save_one(Account(user_id=222, balance=Decimal("0.10")))
    account_updated = await repository.update_one(account_saved)
    assert account_saved == account_updated

@pytest.mark.asyncio
async def test_deve_retornar_none_ao_tentar_atualizar_conta_inexistente(db_session):
    repository = AccountRepository(db_session)    
    account = Account(id=999, user_id=1, balance=Decimal("-100.00"), created_at=datetime.now())
    with pytest.raises(PersistenceException) as e:
        await repository.update_one(account)
    assert "Account não encontrada pelo id: 999" in str(e.value)

@pytest.mark.asyncio
async def test_deve_retornar_lista_vazia_quando_usuario_nao_possui_contas(db_session):
    repository = AccountRepository(db_session)
    accounts = await repository.get_all_by_user_id(user_id=666)
    assert len(accounts) == 0