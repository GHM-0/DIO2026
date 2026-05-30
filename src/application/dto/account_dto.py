# src.application.dto.account_dto.py

from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

class CreateAccountRequest(BaseModel):
    user_id: int = Field(gt=0, description="ID do usuário proprietário da conta")
    balance: Decimal = Field(default=Decimal("0.00"), ge=0, description="Saldo inicial da conta")

class AccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(gt=0,description="ID da conta")
    user_id: int = Field(description="ID do usuário proprietário da conta")
    balance: Decimal = Field(description="Saldo da conta")
    created_at: datetime = Field(description="Data e hora de criação da conta")

class AccountUpdateRequest(BaseModel):
    balance: Decimal = Field(description="Novo saldo da conta")

# class GetAccountResquest(BaseModel):
#     transaction_id: int = Field(gt=0,description="ID da conta")