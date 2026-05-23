from core.exception.entity.entity_exception import EntityException

# Entity
class TransactionException(EntityException):
    pass

# Domain
class InvalidId(TransactionException):
    pass

# Account
class InvalidAccount(TransactionException):
    pass

class SameAccountException(TransactionException):
    pass

class InsufficientFundsException(TransactionException):
    pass

# On Creation
# Amount
class InvalidAmount(TransactionException):
    pass