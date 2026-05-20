import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from application.dto.transaction_dto import CreateTransactionRequest
from core.domain.entity.transaction_entity import Transaction
from core.domain.value_object.transaction_type import TransactionType
from infrastructure.persistence.repository.transaction_repository_impl import TransactionRepository
from infrastructure.exception.persistence.persistence_exception import PersistenceException

@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_transacoes(truncate_table):
    """Garante que a tabela de transações e contas estejam vazias para cada teste."""
    await truncate_table("transactions")

@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_accounts(truncate_table):
    """Garante que a tabela de contas esteja vazia para cada teste."""
    await truncate_table("accounts")

@pytest.mark.asyncio
async def test_deve_salvar_uma_transacao_valida(db_session: AsyncSession, create_account):
    account = await create_account(user_id=1, balance=Decimal("1000.00"))
    repository = TransactionRepository(db_session)
    transaction_dto = CreateTransactionRequest(account_orig_id=account.id, account_dest_id=account.id, type=TransactionType.CREDIT, amount="120.00")
    transaction_save = await repository.save_one(Transaction(**transaction_dto.model_dump()))

    await db_session.commit()

    assert isinstance(transaction_save, Transaction)
    assert transaction_save.account_orig_id == account.id

@pytest.mark.asyncio
async def test_deve_buscar_transacao_por_id(db_session: AsyncSession, create_account):
    account = await create_account(user_id=2)
    repository = TransactionRepository(db_session)
    transaction_dto = CreateTransactionRequest(account_orig_id=account.id, account_dest_id=account.id, type=TransactionType.CREDIT, amount="204.00")
    transaction_save = await repository.save_one(Transaction(**transaction_dto.model_dump()))

    await db_session.commit()
    assert await repository.exists_by_id(transaction_save.id) is True

@pytest.mark.asyncio
async def test_deve_listar_todas_as_transacoes(db_session: AsyncSession, create_account):
    account = await create_account(user_id=3)
    repository = TransactionRepository(db_session)
    t1 = CreateTransactionRequest(account_orig_id=account.id, account_dest_id=account.id, type=TransactionType.CREDIT, amount="204.00")
    t2 = CreateTransactionRequest(account_orig_id=account.id, account_dest_id=account.id, type=TransactionType.CREDIT, amount="200.00")
    await repository.save_one(Transaction(**t1.model_dump()))
    await repository.save_one(Transaction(**t2.model_dump()))
    transactions = await repository.read_all()

    await db_session.commit()
    assert len(transactions) >= 2

@pytest.mark.asyncio
async def test_deve_remover_uma_transacao(db_session: AsyncSession, create_account):
    account = await create_account(user_id=4)
    repository = TransactionRepository(db_session)
    t_dto = CreateTransactionRequest(account_orig_id=account.id, account_dest_id=account.id, type=TransactionType.CREDIT, amount="20.00")
    t_saved = await repository.save_one(Transaction(**t_dto.model_dump()))

    await db_session.commit()
    assert await repository.read_one(t_saved.id) is not None

@pytest.mark.asyncio
async def test_nao_deve_permitir_atualizacao_de_transacao(db_session: AsyncSession, create_account):
    account = await create_account(user_id=5)
    repository = TransactionRepository(db_session)
    t_dto = CreateTransactionRequest(account_orig_id=account.id, account_dest_id=account.id, type=TransactionType.CREDIT, amount="20.00")
    t_saved = await repository.save_one(Transaction(**t_dto.model_dump()))
    with pytest.raises(PersistenceException) as e:
        t_update = Transaction(id=t_saved.id, account_orig_id=t_saved.account_orig_id, account_dest_id=t_saved.account_dest_id, type=TransactionType.DEBIT, amount=t_saved.amount)
        await repository.update_one(t_update)
    assert str(e.value) == "Uma Transaction não pode ser alterada após o registro."

@pytest.mark.asyncio
async def test_deve_retornar_transacoes_by_account_id(db_session: AsyncSession, create_account):
    account = await create_account(user_id=6)
    repository = TransactionRepository(db_session)
    t_dto = CreateTransactionRequest(account_orig_id=account.id, account_dest_id=account.id, type=TransactionType.CREDIT, amount="204.00")
    await repository.save_one(Transaction(**t_dto.model_dump()))

    await db_session.commit()
    transactions = await repository.get_all_by_account_id(account_id=account.id)
    assert len(transactions) >= 1

@pytest.mark.asyncio
async def test_deve_retornar_lista_vazia_quando_by_account_id_nao_for_encontrado(db_session: AsyncSession):
    repository = TransactionRepository(db_session)
    transactions = await repository.get_all_by_account_id(account_id=9999)
    assert len(transactions) == 0