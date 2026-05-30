# tests/helper/integration_fixtures.py

import pytest
import pytest_asyncio
from decimal import Decimal
from typing import AsyncGenerator, AsyncIterator, Callable, Awaitable

from sqlalchemy import text, NullPool
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from core.domain.entity.account_entity import Account
from core.domain.entity.transaction_entity import Transaction
from infrastructure.config import settings
from infrastructure.persistence.async_sqlalchemy_database import AsyncSqlAlchemyDatabase
from infrastructure.persistence.model.base_model import Base
from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from infrastructure.persistence.repository.transaction_repository_impl import TransactionRepository
from infrastructure.persistence.sqlalchemy_transaction_unit import AsyncSqlAlchemyTransactionUnit

# ==============================================================================
# 1. CONFIGURAÇÃO DE AMBIENTE (DATABASE URLS)
# ==============================================================================

@pytest.fixture(scope="session")
def db_root_url() -> str:
    return (
        f"mysql+pymysql://root:{settings.MYSQL_ROOT_PASSWORD}@"
        f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/"
    )

@pytest.fixture(scope="session")
def db_url() -> str:
    return (
        f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWORD}@"
        f"{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DATABASE}"
        f"?charset={settings.CHARSET}"
    )

# ==============================================================================
# 2. INFRAESTRUTURA DE PERSISTÊNCIA (SQLALCHEY / UOW)
# ==============================================================================

@pytest_asyncio.fixture(scope="function")
async def db_instance(db_url: str) -> AsyncGenerator[AsyncSqlAlchemyDatabase, None]:
    db = AsyncSqlAlchemyDatabase(db_url)
    db._engine = create_async_engine(db_url, poolclass=NullPool)
    db._session_factory = async_sessionmaker(bind=db._engine, expire_on_commit=False)

    async with db._engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield db
    await db.disconnect()

@pytest.fixture(scope="function")
def engine(db_instance: AsyncSqlAlchemyDatabase):
    return db_instance._engine

@pytest_asyncio.fixture(scope="function")
async def db_session(db_instance: AsyncSqlAlchemyDatabase) -> AsyncIterator[AsyncSession]:
    async with db_instance.get_session() as session:
        yield session

@pytest.fixture(scope="function")
def uow(db_instance: AsyncSqlAlchemyDatabase) -> AsyncSqlAlchemyTransactionUnit:
    return AsyncSqlAlchemyTransactionUnit(db_instance)

# ==============================================================================
# 3. GERENCIAMENTO DE ESTADO (CLEANUP)
# ==============================================================================

@pytest.fixture(scope="function")
def truncate_table(engine) -> Callable[[str], Awaitable[None]]:
    async def _truncate(table_name: str):
        async with engine.begin() as conn:
            await conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            await conn.execute(text(f"TRUNCATE TABLE {table_name};"))
            await conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
    return _truncate

# ==============================================================================
# 4. FACTORIES DE DOMÍNIO (HELPERS)
# ==============================================================================

@pytest_asyncio.fixture(scope="function")
async def create_account(db_session: AsyncSession):
    """Cria uma conta e persiste no banco para uso em testes."""
    async def _create(user_id: int, balance: Decimal = Decimal("0.00")):
        repo = AccountRepository(db_session)
        account = Account(user_id=user_id, balance=balance)
        saved = await repo.save_one(account)
        await db_session.commit()
        return saved
    return _create

@pytest_asyncio.fixture(scope="function")
async def db_to_test(db_session: AsyncSession):
    """Seed de dados complexos (Contas + Transações)."""
    async def _seed(data: list[dict]):
        account_repo = AccountRepository(db_session)
        transaction_repo = TransactionRepository(db_session)
        created_data = []

        for account_data in data:
            account = Account(
                user_id=account_data.get("user_id", 1),
                balance=Decimal(str(account_data.get("balance", "0.00")))
            )
            account_saved = await account_repo.save_one(account)

            transactions = []
            for tx_data in account_data.get("transactions", []):
                tx = Transaction(
                    account_orig_id=account_saved.id,
                    account_dest_id=tx_data.get("account_dest_id"),
                    amount=Decimal(str(tx_data["amount"])),
                    transaction_type=tx_data["transaction_type"]
                )
                tx_saved = await transaction_repo.save_one(tx)
                transactions.append(tx_saved)

            created_data.append({"account": account_saved, "transactions": transactions})

        await db_session.commit()
        return created_data
    return _seed

# ==============================================================================
# 5. APOIO À CAMADA DE APRESENTAÇÃO (API / SECURITY)
# ==============================================================================

@pytest.fixture(scope="function")
def api_client(db_instance):
    from fastapi.testclient import TestClient
    from main import app
    from presentation.api.controllers.account_controller import get_uow as get_uow_acc
    from presentation.api.controllers.transaction_controller import get_uow as get_uow_tx

    def override_get_uow():
        return AsyncSqlAlchemyTransactionUnit(db_instance)

    app.dependency_overrides[get_uow_acc] = override_get_uow
    app.dependency_overrides[get_uow_tx] = override_get_uow

    with TestClient(app, raise_server_exceptions=True) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def setup_security_settings(monkeypatch):
    test_secret = "00000000000000000000000000000001"
    test_algorithm = "HS256"
    monkeypatch.setattr("infrastructure.security.security.SECRET", test_secret)
    monkeypatch.setattr("infrastructure.security.security.ALGORITHM", test_algorithm)
    return {"secret": test_secret, "algorithm": test_algorithm}

@pytest.fixture
def authenticated_headers(api_client):
    def _authenticated_headers_factory(user_id_value: int):
        auth_response = api_client.post("/auth/login", json={"user_id": user_id_value})
        auth_response.raise_for_status()
        token = auth_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    return _authenticated_headers_factory