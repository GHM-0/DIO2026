import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from core.domain.entity.credit_entity import Credit
from core.domain.entity.debit_entity import Debit
from core.domain.entity.transaction_entity import Transaction
from core.domain.entity.transference_entity import Transference

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

# Criação direta
@pytest.mark.asyncio
async def test_deve_salvar_uma_transacao_valida(db_session: AsyncSession, create_account):
    account1 = await create_account(user_id=1, balance=Decimal("1000.00"))
    account2 = await create_account(user_id=1, balance=Decimal("1000.00"))

    repository = TransactionRepository(db_session)

    t= Transference.create(account_orig=account1,account_dest=account2,amount=Decimal("10.00"))

    transaction_save = await repository.save_one(t)

    await db_session.commit()

    assert isinstance(transaction_save, Transaction)
    assert transaction_save.account_orig_id == account1.id
    assert transaction_save.account_dest_id == account2.id

# Criação Indireta Simula Operação de Caso de Uso
@pytest.mark.asyncio
async def test_deve_salvar_uma_transacao_valida_indireta(db_session: AsyncSession, create_account): # Renomeado para evitar conflito
    account1 = await create_account(user_id=1, balance=Decimal("1000.00"))
    account2 = await create_account(user_id=1, balance=Decimal("1000.00"))

    repository = TransactionRepository(db_session)

    debit = Debit.create(account_orig=account1,account_dest=account2,amount=Decimal("10.00"))
    credit = Credit.create(account_orig=account1,account_dest=account2,amount=Decimal("10.00"))

    t= Transference(account_orig_id=account1.id,account_dest_id=account2.id,amount=Decimal("10.00"))

    transaction_save1 = await repository.save_one(debit)
    transaction_save2 = await repository.save_one(credit)
    transaction_save = await repository.save_one(t)

    await db_session.commit()

    assert isinstance(transaction_save, Transaction)
    assert transaction_save.account_orig_id == account1.id
    assert transaction_save.account_dest_id == account2.id


@pytest.mark.asyncio
async def test_deve_buscar_transacao_por_id(db_session: AsyncSession, create_account):

    account1 = await create_account(user_id=1, balance=Decimal("1000.00"))
    account2 = await create_account(user_id=1, balance=Decimal("1000.00"))

    repository = TransactionRepository(db_session)

    t= Transference.create(account_orig=account1,account_dest=account2,amount=Decimal("10.00"))

    transaction_save = await repository.save_one(t)

    await db_session.commit()

    assert await repository.exists_by_id(transaction_save.id) is True

@pytest.mark.asyncio
async def test_deve_listar_todas_as_transacoes(db_session: AsyncSession, create_account):

    account1 = await create_account(user_id=111, balance=Decimal("1000.00"))
    account2 = await create_account(user_id=222, balance=Decimal("1000.00"))

    transaction_repository = TransactionRepository(db_session)

    t1 = Transference.create(account_orig=account1, account_dest=account2, amount=Decimal("204.00"))
    t2 = Transference.create(account_orig=account1, account_dest=account2, amount=Decimal("200.00"))

    await transaction_repository.save_one(t1)
    await transaction_repository.save_one(t2)

    transactions = await transaction_repository.read_all()

    await db_session.commit()

    assert len(transactions) >= 2

@pytest.mark.asyncio
async def test_deve_remover_uma_transacao(db_session: AsyncSession, create_account):

    account1 = await create_account(user_id=41, balance=Decimal("1000.00"))
    account2 = await create_account(user_id=61, balance=Decimal("1000.00"))

    repository = TransactionRepository(db_session)


    t1 = Transference.create(account_orig=account1, account_dest=account2, amount=Decimal("204.00"))


    t_saved = await repository.save_one(t1)

    await db_session.commit()
    assert await repository.read_one(t_saved.id) is not None
    assert await repository.remove_one(t_saved.id) is True
    assert await repository.read_one(t_saved.id) is None


@pytest.mark.asyncio
async def test_nao_deve_permitir_atualizacao_de_transacao(db_session: AsyncSession, create_account):
        account1 = await create_account(user_id=401, balance=Decimal("1000.00"))
        account2 = await create_account(user_id=6100, balance=Decimal("10.00"))

        repository = TransactionRepository(db_session)

        t1 = Transference.create(account_orig=account1, account_dest=account2, amount=Decimal("204.00"))

        t_saved = await repository.save_one(t1)

        await db_session.commit()

        with pytest.raises(PersistenceException) as e:
            t_update = Transference(account_orig_id=account1.id, account_dest_id=account2.id, amount=Decimal("999.99"))
            await repository.update_one(t_update)
        assert str(e.value) == "Uma Transaction não pode ser alterada após o registro."

@pytest.mark.asyncio
async def test_deve_retornar_transacoes_by_account_id(db_session: AsyncSession, create_account):
    account1 = await create_account(user_id=401, balance=Decimal("1000.00"))
    account2 = await create_account(user_id=6100, balance=Decimal("10.00"))

    repository = TransactionRepository(db_session)

    t1 = Transference.create(account_orig=account1, account_dest=account2, amount=Decimal("204.00"))

    t_saved = await repository.save_one(t1)

    await db_session.commit()
    transactions = await repository.get_all_by_account_id(account_id=account1.id)
    assert len(transactions) >= 1

@pytest.mark.asyncio
async def test_deve_retornar_lista_vazia_quando_by_account_id_nao_for_encontrado(db_session: AsyncSession):
    repository = TransactionRepository(db_session)
    transactions = await repository.get_all_by_account_id(account_id=9999)
    assert len(transactions) == 0