# src.application.dto.transaction_dto.py
from typing import Optional

import optional
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime

from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType

class CreateTransactionRequest(BaseModel):
    account_orig_id: int = Field(gt=0, description="ID da conta de Origem")
    account_dest_id: int = Field(gt=0, description="ID da conta de Destino (Opcional para Depósito/Saque)") # Tornar opcional
    type: TransactionType = Field(description="Tipo de Operação")
    amount: Decimal = Field(default=Decimal("0.00"), ge=0, description="Valor da transação")

class TransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int = Field(gt=0, description="ID da transação")
    account_orig_id: int = Field(gt=0, description="ID da conta de Origem")
    account_dest_id: int = Field(gt=0, description="ID da conta de Destino (Opcional para Depósito/Saque)") # Tornar opcional
    type: TransactionType = Field(description="Tipo de Operação")
    amount: Decimal = Field(gt=0, description="Valor da transação")
    timestamp: datetime = Field(description="Data e Hora da transação - UTC")
    status: TransactionStatus = Field(description="Estado da Transação")
    message: Optional[str] = Field(description="Mensagem Opcional", default=None)

# class GetTransactionRequest(BaseModel):
#     transaction_id: int = Field(gt=0, description="ID da transação")