# src.core.domain.value_object.balance.py

from decimal import Decimal
from typing import Any
from exception.core.exception.value_object.balance_exception import InvalidBalance

class Balance:
    @staticmethod
    def validate(value: Any) -> Decimal:
        if value is None:
            raise InvalidBalance("O saldo não pode ser nulo")
        
        try:
            return Decimal(str(value))
        except (ValueError, TypeError):
            raise InvalidBalance("O saldo deve ser um número válido")