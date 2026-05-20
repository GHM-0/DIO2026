import pytest
from decimal import Decimal
from infrastructure.persistence.sqlalchemy_transaction_unit import AsyncSqlAlchemyTransactionUnit
from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from core.domain.entity.account_entity import Account

@pytest.mark.asyncio
async def test_uow_commit_successfully(db_instance, truncate_table):
    """Garante que as alterações são persistidas ao final do bloco with se não houver erro."""
    await truncate_table("accounts")
    uow = AsyncSqlAlchemyTransactionUnit(db_instance)
    
    user_id = 123
    balance = Decimal("500.00")
    
    async with uow:
        repo = uow.get_repository(AccountRepository)
        account = Account(user_id=user_id, balance=balance)
        await repo.save_one(account)
        # O commit deve ocorrer automaticamente ao sair do bloco com sucesso
        
    # Verificação: Abrir uma nova sessão/UoW para ver se o dado está lá
    async with uow:
        repo = uow.get_repository(AccountRepository)
        accounts = await repo.get_all_by_user_id(user_id)
        assert len(accounts) == 1
        assert accounts[0].balance == balance

@pytest.mark.asyncio
async def test_uow_rollback_on_exception(db_instance, truncate_table):
    """Garante que as alterações são revertidas se ocorrer uma exceção dentro do bloco."""
    await truncate_table("accounts")
    uow = AsyncSqlAlchemyTransactionUnit(db_instance)
    
    user_id = 456
    
    try:
        async with uow:
            repo = uow.get_repository(AccountRepository)
            account = Account(user_id=user_id, balance=Decimal("100.00"))
            await repo.save_one(account)
            
            # Simulando um erro inesperado
            raise RuntimeError("Erro forçado para testar rollback")
    except RuntimeError:
        pass
        
    # Verificação: O dado NÃO deve existir no banco
    async with uow:
        repo = uow.get_repository(AccountRepository)
        accounts = await repo.get_all_by_user_id(user_id)
        assert len(accounts) == 0

@pytest.mark.asyncio
async def test_uow_repository_cache(db_instance):
    """Garante que o get_repository retorna a mesma instância (cache) dentro da mesma transação."""
    uow = AsyncSqlAlchemyTransactionUnit(db_instance)
    
    async with uow:
        repo1 = uow.get_repository(AccountRepository)
        repo2 = uow.get_repository(AccountRepository)
        
        assert repo1 is repo2
        assert repo1._session is repo2._session

@pytest.mark.asyncio
async def test_uow_raises_error_outside_context(db_instance):
    """Garante que tentar obter um repositório fora do contexto 'with' lança erro."""
    uow = AsyncSqlAlchemyTransactionUnit(db_instance)
    
    with pytest.raises(RuntimeError, match="Transação não iniciada"):
        uow.get_repository(AccountRepository)
