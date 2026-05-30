# src.core.domain.value_object.transaction_result.py

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from core.domain.value_object.transaction_status import TransactionStatus
from core.domain.value_object.transaction_type import TransactionType

@dataclass(frozen=True)
class TransactionResult:
    """
    Representa o resultado imutável de uma operação de transação financeira.
    
    Carrega informações completas sobre o estado final da operação para 
    fins de auditoria e resposta de processamento.
    """
    status: TransactionStatus
    message: str
    transaction_id: int | None
    transaction_type: TransactionType
    amount: Decimal
    account_orig_id: int | None
    account_dest_id: int | None
    timestamp: datetime
