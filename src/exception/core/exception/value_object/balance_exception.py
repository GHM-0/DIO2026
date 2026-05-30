from exception.core.exception.value_object.value_object_exception import ValueObjectException

class BalanceException(ValueObjectException):
    pass

class InvalidBalance(BalanceException):
    ...
