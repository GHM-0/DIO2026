from enum import Enum

class TransactionStatus(Enum):
     CREATED = "Pending"
     COMPLETED = "Concluded"
     FAILED = "Failed"
     REVERTED = "Reverted"