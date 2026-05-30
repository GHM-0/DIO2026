from exception.core.exception.entity.entity_exception import EntityException

# Entity
class AccountException(EntityException):
    pass

# Domain
class InvalidId(AccountException):
    pass

# User_id
class InvalidUser(AccountException):
    pass

class InsufficientFundsException(AccountException):
    pass

# Withdraw
class InsufficientBalance(AccountException):
    pass

# Security/Ownership
class UnauthorizedUser(AccountException):
    """Lançada quando um usuário tenta operar uma conta da qual não é titular."""
    pass
