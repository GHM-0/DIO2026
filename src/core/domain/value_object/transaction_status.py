# src.core.domain.value_object.transaction_type.py

from enum import Enum

class TransactionStatus(Enum):
     CREATED = "Pending"
     COMPLETED = "Concluded"
     FAILED = "Failed"
     REVERTED = "Reverted"