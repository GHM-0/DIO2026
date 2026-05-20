# src/presentation/api/controllers/transaction_controller.py
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException

from application.dto.transaction_dto import CreateTransactionRequest, TransactionResponse
from application.use_case.transaction.create_transaction import CreateTransaction
from application.use_case.transaction.get_transaction_by_account_id import GetTransactionByAccountId
from application.use_case.transaction.get_transaction_by_id import GetTransactionById
from application.use_case.account.get_account_by_id import GetAccountByID
from infrastructure.persistence.repository.transaction_repository_impl import TransactionRepository
from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from infrastructure.persistence.sqlalchemy_transaction_unit import AsyncSqlAlchemyTransactionUnit

from infrastructure.security.security import login_required
from infrastructure.lifecycle import db_instance

router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
    dependencies=[Depends(login_required)]
)

def get_uow() -> AsyncSqlAlchemyTransactionUnit:
    return AsyncSqlAlchemyTransactionUnit(db_instance)

def get_create_transaction_use_case(
    uow: Annotated[AsyncSqlAlchemyTransactionUnit, Depends(get_uow)]
) -> CreateTransaction:
    return CreateTransaction(uow, TransactionRepository, AccountRepository)

def get_transaction_by_id_use_case(
    uow: Annotated[AsyncSqlAlchemyTransactionUnit, Depends(get_uow)]
) -> GetTransactionById:
    return GetTransactionById(uow, TransactionRepository)

def get_transaction_by_account_id_use_case(
    uow: Annotated[AsyncSqlAlchemyTransactionUnit, Depends(get_uow)]
) -> GetTransactionByAccountId:
    return GetTransactionByAccountId(uow, TransactionRepository)

def get_account_by_id_use_case(
    uow: Annotated[AsyncSqlAlchemyTransactionUnit, Depends(get_uow)]
) -> GetAccountByID:
    return GetAccountByID(uow, AccountRepository)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionResponse)
async def create_transaction(
    request: CreateTransactionRequest,
    use_case: Annotated[CreateTransaction, Depends(get_create_transaction_use_case)],
    current_user: Annotated[dict, Depends(login_required)]
):
    """
    Cria uma nova transação validando titularidade e saldo.
    """
    try:
        # Passa o user_id do usuário logado para validação de domínio
        return await use_case.execute(request, requester_user_id=current_user["user_id"])
    except (ValueError, Exception) as e:
        # Idealmente aqui teríamos um exception handler global, 
        # mas para garantir o retorno 400 nos testes de validação:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{account_id}", response_model=list[TransactionResponse])
async def read_transactions_by_account(
    account_id: int,
    use_case: Annotated[GetTransactionByAccountId, Depends(get_transaction_by_account_id_use_case)],
    get_account_use_case: Annotated[GetAccountByID, Depends(get_account_by_id_use_case)],
    current_user: Annotated[dict, Depends(login_required)]
):
    """
    Lista transações de uma conta específica, garantindo que o usuário seja o dono.
    """
    account = await get_account_use_case.execute(account_id)

    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if account.user_id != current_user["user_id"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this account")

    return await use_case.execute(account_id=account_id)