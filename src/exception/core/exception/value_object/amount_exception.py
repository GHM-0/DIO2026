from exception.core.exception.value_object.value_object_exception import ValueObjectException


class AmountException(ValueObjectException):
    pass

class InvalidAmount(AmountException):
    ...
