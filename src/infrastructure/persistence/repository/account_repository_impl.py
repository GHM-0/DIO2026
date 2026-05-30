# src.infrastructure.database.repository.account_repository_impl.py
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select, delete, Delete, CursorResult
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.engine import  Result, ScalarResult

from core.domain.entity.account_entity import Account
from core.domain.port.repository.account_repository_interface import IAccountRepository

from exception.infrastructure.exception.persistence.persistence_exception import PersistenceException
from infrastructure.persistence.model.account_model import AccountModel


class AccountRepository(IAccountRepository):

    _IMMUTABLE_FIELDS = {"account_id", "user_id", "created_at"} # Define immutable fields for AccountModel

    def __init__(self,session: AsyncSession):
        self._session = session

    @staticmethod
    def _to_entity(model:AccountModel) -> Account:

        return Account(
            account_id = model.id,
            user_id = model.user_id,
            balance = model.balance,
            created_at = model.created_at
        )

    async def exists_by_id(self, account_id: int) -> bool:
        """Verifica existência de forma otimizada (SELECT ID)."""

        query: Select[tuple[int]] = select(AccountModel.id).where(AccountModel.id == account_id)
        result: Result[tuple[int]] = await self._session.execute(query)
        
        return result.first() is not None

    async def read_all(self) -> List[Account]:
        """Busca todos os registros."""

        query: Select[tuple[AccountModel]] = select(AccountModel).order_by(AccountModel.created_at.asc(), AccountModel.id.asc())
        result: Result[tuple[AccountModel]] = await self._session.execute(query)
        models: ScalarResult[AccountModel] = result.scalars()

        return [self._to_entity(model) for model in models if model is not None]

    async def read_all_paginated(self, limit: int, skip: int) -> List[Account]:
        """Busca todos os registros com paginação."""

        query = select(AccountModel).limit(limit).offset(skip)
        result = await self._session.execute(query)
        models: ScalarResult[AccountModel] = result.scalars()

        return [self._to_entity(model) for model in models if model is not None]

    async def read_one(self, account_id: int) -> Optional[Account]:
        """Recupera uma única entidade pelo ID."""

        query: Select[tuple[AccountModel]] = select(AccountModel).where(AccountModel.id == account_id)
        result: Result[tuple[AccountModel]] = await self._session.execute(query)
        model: Optional[AccountModel] = result.scalar_one_or_none()

        return self._to_entity(model) if model else None

    async def save_one(self, entity: Account) -> Account:
        """Persiste o estado de uma entidade."""

        model = AccountModel(
            user_id = entity.user_id,
            balance = entity.balance,
            created_at = entity.created_at
        )
        
        try:
            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)
        except IntegrityError as e:

            raise PersistenceException(f"Conflito de dados ao criar {Account.__name__}: {str(e)}")
        except OperationalError as e:

            raise PersistenceException(f"Erro de infraestrutura ao acessar o banco: {str(e)}")
        except SQLAlchemyError as e:

            raise PersistenceException(f"Erro inesperado no banco de dados: {str(e)}")

        return self._to_entity(model)

    async def update_one(self, entity: Account) -> Optional[Account]:
        """
        Sincroniza o estado da Entidade com o banco de dados.
        Apenas campos mutáveis são atualizados.
        """
        if entity.id is None:
            raise PersistenceException("ID da entidade é obrigatório para atualização.")

        try:

            query: Select[tuple[AccountModel]] = select(AccountModel).where(AccountModel.id == entity.id)
            result: Result[tuple[AccountModel]] = await self._session.execute(query)
            model: Optional[AccountModel] = result.scalar_one_or_none()

            if not model:
                raise PersistenceException(f"{Account.__name__} não encontrada pelo account_id: {entity.id}")

            for column in AccountModel.__table__.columns:
                field_name = column.name
                if field_name not in self._IMMUTABLE_FIELDS:

                    setattr(model, field_name, getattr(entity, field_name))

            await self._session.flush()
            await self._session.refresh(model)

            return self._to_entity(model)

        except SQLAlchemyError as e:
            raise PersistenceException(
                f"Erro ao atualizar {Account.__name__} acount_id:{entity.id}. Detalhes: {str(e)}"
            )

    async def remove_one(self, account_id: int) -> bool:
        """Exclui permanentemente um registro."""
        deleted: Delete = delete(AccountModel).where(AccountModel.id == account_id)

        try:

           result: Result[tuple[AccountModel]] = await self._session.execute(deleted)

           if not isinstance(result, CursorResult):
               raise PersistenceException(
                   f"Tipo de resultado inesperado ao remover {Account.__name__} account_id:{account_id}"
               )

           if result.rowcount is not None:
               if result.rowcount > 1:
                   raise PersistenceException(
                       f"Erro de integridade: a tentativa de remover {Account.__name__}  account_id:{account_id} "
                       f"afetaria {result.rowcount} linhas. Operação abortada."
                   )

               await self._session.flush()
               return (result.rowcount == 1)

        except SQLAlchemyError as e:
            raise PersistenceException(f"Falha ao remover {Account.__name__}  account_id:{account_id}. Erro original: {str(e)}")

    async def get_all_by_user_id(self, user_id: int) -> List[Account]:

        query: Select[tuple[AccountModel]] = select(AccountModel).where(AccountModel.user_id == user_id).order_by(AccountModel.created_at.asc(), AccountModel.id.asc())
        result: Result[tuple[AccountModel]] = await self._session.execute(query)
        models: ScalarResult[AccountModel] = result.scalars()

        return [self._to_entity(model) for model in models if model is not None]

    async def get_all_by_user_id_paginated(self, user_id: int,limit:int,skip:int) -> List[Account]:

        query: Select[tuple[AccountModel]] = select(AccountModel).where(AccountModel.user_id == user_id).order_by(AccountModel.created_at.asc(), AccountModel.id.asc()).limit(limit).offset(skip)
        result: Result[tuple[AccountModel]] = await self._session.execute(query)
        models: ScalarResult[AccountModel] = result.scalars()

        return [self._to_entity(model) for model in models if model is not None]