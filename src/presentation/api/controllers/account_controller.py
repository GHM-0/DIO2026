# src/presentation/api/controllers/account_controller.py
from typing import Annotated
from fastapi import APIRouter, Depends, status

from application.dto.account_statement_dto import AccountStatementResponse
from application.use_case.account.get_account_by_id import GetAccountByID
from application.use_case.account.get_account_by_user_id import GetAccountsByUserId
from application.use_case.get_account_statement import GetAccountStatement
from infrastructure.persistence.repository.account_repository_impl import AccountRepository
from infrastructure.persistence.repository.transaction_repository_impl import TransactionRepository
from infrastructure.persistence.sqlalchemy_transaction_unit import AsyncSqlAlchemyTransactionUnit
from application.dto.account_dto import AccountResponse, CreateAccountRequest
from application.use_case.account.create_account import CreateAccount

from infrastructure.security.security import login_required

from infrastructure.lifecycle import db_instance

router = APIRouter(
    prefix="/accounts", 
    tags=["Accounts"],
    dependencies=[Depends(login_required)]
)

# Dependency Provider para a UoW
def get_uow() -> AsyncSqlAlchemyTransactionUnit:
    return AsyncSqlAlchemyTransactionUnit(db_instance)

# Provider para o Use Case Para este route
def get_account_use_case(
    uow: Annotated[AsyncSqlAlchemyTransactionUnit, Depends(get_uow)]
) -> CreateAccount:
    return CreateAccount(uow,AccountRepository)

def get_account_by_id_use_case(
    uow: Annotated[AsyncSqlAlchemyTransactionUnit, Depends(get_uow)]
) -> GetAccountByID:
    return GetAccountByID(uow,AccountRepository)

def get_account_by_user_id_use_case(
    uow: Annotated[AsyncSqlAlchemyTransactionUnit, Depends(get_uow)]
) -> GetAccountsByUserId:
    return GetAccountsByUserId(uow,AccountRepository)

def get_account_statement(
    uow: Annotated[AsyncSqlAlchemyTransactionUnit, Depends(get_uow)]
) -> GetAccountStatement:
    return GetAccountStatement(uow,AccountRepository,TransactionRepository)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=AccountResponse)
async def create_account(
    request: CreateAccountRequest,                                     # Via Body
    use_case: Annotated[CreateAccount, Depends(get_account_use_case)]
):
    """
    Cria uma nova conta bancária.
    """
    return await use_case.execute(request)


# Dependo Do Login
@router.get("/", response_model=list[AccountResponse])
async def read_accounts(
    use_case: Annotated[GetAccountsByUserId, Depends(get_account_by_user_id_use_case)],
    current_user: Annotated[dict, Depends(login_required)],
    limit: int = 10,
    skip: int = 0
):
    return await use_case.execute(user_id=current_user["user_id"], limit=limit, skip=skip)

@router.get("/{id}/transactions", response_model=AccountStatementResponse)
async def read_account_transactions(
        use_case: Annotated[GetAccountStatement, Depends(get_account_statement)],
        id: int, limit: int, skip: int = 0):
    return await use_case.execute(account_id=id, limit=limit, skip=skip)