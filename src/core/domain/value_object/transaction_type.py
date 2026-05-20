# src.core.domain.value_object.transaction_type.py
from enum import Enum

class TransactionType(Enum):
    CREDIT = "Deposit"
    DEBIT = "Withdraw"
    TRANSFERENCE = "Transference"
