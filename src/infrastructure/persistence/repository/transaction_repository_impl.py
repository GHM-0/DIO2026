# src.infrastructure.database.repository.transaction_repository_impl.py
from typing import Optional, List, Dict, Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, Select, delete, Delete, CursorResult
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.engine import Result, ScalarResult

from core.domain.entity.credit_entity import Credit
from core.domain.entity.debit_entity import Debit
from core.domain.entity.transaction_entity import Transaction
from core.domain.entity.transference_entity import Transference
from core.domain.port.repository.transaction_repository_interface import ITransactionRepository
from core.domain.value_object.transaction_type import TransactionType

from exception.infrastructure.exception.persistence.persistence_exception import PersistenceException
from infrastructure.persistence.model.transaction_model import TransactionModel


class TransactionRepository(ITransactionRepository):

    # NOTA: No design atual um Transação é imutável.
    _IMMUTABLE_FIELDS = {"transaction_id", "account_orig_id", "account_dest_id", "timestamp", "transaction_type", "amount", "transaction_status"}


    def __init__(self,session: AsyncSession):
        self._session = session

    @staticmethod
    def _to_entity(model:TransactionModel) -> Transaction:

        try:

         transaction_map:Dict[TransactionType,Type[Transaction]] = {
             TransactionType.TRANSFERENCE: Transference,
             TransactionType.CREDIT: Credit,
             TransactionType.DEBIT: Debit,
         }

         transaction_class = transaction_map[model.transaction_type]
         return transaction_class(
             transaction_id=model.id,
             account_orig_id=model.account_orig_id,
             account_dest_id=model.account_dest_id,
             amount=model.amount,
             timestamp=model.timestamp,
             status=model.transaction_status
         )

        except Exception as e:
            raise PersistenceException(
                f"Dados inconsistentes no DB para a {Transaction.__name__} transaction_id:{model.id}. "
                f"Erro: {str(e)}"
            )

    async def exists_by_id(self, transaction_id: int) -> bool:
        """Verifica existência de forma otimizada (SELECT ID)."""
        query: Select[tuple[int]] = select(TransactionModel.id).where(TransactionModel.id == transaction_id)
        result: Result[tuple[int]] = await self._session.execute(query)

        return result.first() is not None

    async def read_all(self) -> List[Transaction]:
        """Busca todos os registros."""

        query: Select[tuple[TransactionModel]] = select(TransactionModel).order_by(TransactionModel.timestamp.asc())
        result: Result[tuple[TransactionModel]] = await self._session.execute(query)
        models: ScalarResult[TransactionModel] = result.scalars()

        return [self._to_entity(model) for model in models if model is not None]

    async def read_all_paginated(self, limit: int, skip: int) -> List[Transaction]:
        """Busca todos os registros com paginação."""

        query: Select[tuple[TransactionModel]] = select(TransactionModel).limit(limit).offset(skip)
        result: Result[tuple[TransactionModel]] = await self._session.execute(query)
        models: ScalarResult[TransactionModel] = result.scalars()

        return [self._to_entity(model) for model in models if model is not None]

    async def read_one(self, transaction_id: int) -> Optional[Transaction]:
        """Recupera uma única entidade pelo ID."""

        query: Select[tuple[TransactionModel]] = select(TransactionModel).where(TransactionModel.id == transaction_id)
        result: Result[tuple[TransactionModel]] = await self._session.execute(query)
        model: Optional[TransactionModel] = result.scalar_one_or_none()

        return self._to_entity(model) if model else None

    async def save_one(self, entity: Transaction) -> Transaction:
        """Persiste o estado de uma transação."""
        model = TransactionModel(
            account_orig_id = entity.account_orig_id,
            account_dest_id = entity.account_dest_id,
            transaction_type = entity.type,
            amount = entity.amount,
            timestamp = entity.timestamp,
            transaction_status = entity.status
        )

        try:
            self._session.add(model)
            await self._session.flush()
            await self._session.refresh(model)

        except IntegrityError as e:
            raise PersistenceException(f"Erro de integridade ao salvar transação: {str(e)}")
        except OperationalError as e:
            raise PersistenceException(f"Erro de infraestrutura ao acessar o banco: {str(e)}")
        except SQLAlchemyError as e:
            raise PersistenceException(f"Falha ao persistir {Transaction.__name__}. Detalhes: {str(e)}")

        return self._to_entity(model)

    async def update_one(self, entity: Transaction) -> Optional[Transaction]:
        """
        Bloqueio de atualização por design.
        Transações financeiras são imutáveis.
        """
        raise PersistenceException(f"Uma {Transaction.__name__} não pode ser alterada após o registro.")

    async def remove_one(self, transaction_id: int) -> bool:
        """
        Exclui permanentemente um registro.
        """
        deleted: Delete = delete(TransactionModel).where(TransactionModel.id == transaction_id)

        try:
           result: Result[tuple[TransactionModel]] = await self._session.execute(deleted)

           if not isinstance(result, CursorResult):
               raise PersistenceException(
                   f"Tipo de resultado inesperado ao remover {Transaction.__name__} transaction_id:{transaction_id}"
               )

           if result.rowcount > 1:
               raise PersistenceException(
                   f"Erro de integridade crítica: a tentativa de remover {Transaction.__name__} transaction_id:{transaction_id} "
                   f"afetaria múltiplas linhas ({result.rowcount}). Operação abortada."
               )

           await self._session.flush()
           return result.rowcount == 1

        except SQLAlchemyError as e:
            raise PersistenceException(f"Falha ao remover {Transaction.__name__} transaction_id:{transaction_id}. Erro: {str(e)}")

    async def get_all_by_account_id(self, account_id: int) -> List[Transaction]:
        """Recupera o extrato de uma conta específica (como origem ou destino)."""

        query: Select[tuple[TransactionModel]] = select(TransactionModel).where(
            (TransactionModel.account_orig_id == account_id) |
            (TransactionModel.account_dest_id == account_id)
        ).order_by(TransactionModel.timestamp.asc(), TransactionModel.id.asc())

        result: Result[tuple[TransactionModel]] = await self._session.execute(query)
        models: ScalarResult[TransactionModel] = result.scalars()

        return [self._to_entity(model) for model in models if model is not None]

    async def get_all_by_account_id_paginated(self, account_id: int,limit:int,skip:int) -> List[Transaction]:
        """Recupera o extrato de uma conta específica com paginação."""

        query: Select[tuple[TransactionModel]] = select(TransactionModel).where(
             (TransactionModel.account_orig_id == account_id) |
             (TransactionModel.account_dest_id == account_id)
        ).order_by(TransactionModel.timestamp.asc(), TransactionModel.id.asc()).limit(limit).offset(skip)

        result: Result[tuple[TransactionModel]] = await self._session.execute(query)
        models: ScalarResult[TransactionModel] = result.scalars()

        return [self._to_entity(model) for model in models if model is not None]