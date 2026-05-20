# src/application/dto/account_statement_dto.py

from pydantic import BaseModel
from typing import List
from application.dto.account_dto import AccountResponse
from application.dto.transaction_dto import TransactionResponse

class AccountStatementResponse(BaseModel):
    account: AccountResponse
    transactions: List[TransactionResponse]