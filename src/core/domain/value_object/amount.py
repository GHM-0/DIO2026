# src.core.domain.value_object.amount.py

from decimal import Decimal
from typing import Any
from exception.core.exception.value_object.amount_exception import InvalidAmount

class Amount:
    @staticmethod
    def validate(value: Any) -> Decimal:
        if value is None:
            raise InvalidAmount("O valor não pode ser nulo")
        
        try:
            decimal_value = Decimal(str(value))
        except (ValueError, TypeError):
            raise InvalidAmount("O valor deve ser um número válido")

        if decimal_value <= 0:
            raise InvalidAmount("O valor deve ser positivo")
        
        return decimal_value