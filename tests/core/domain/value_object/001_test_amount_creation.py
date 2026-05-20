from decimal import Decimal

import pytest

from core.domain.value_object.amount import Amount
from core.exception.value_object.amount_exception import InvalidAmount


# Formatação Simples
@pytest.mark.parametrize("value, formated",[
    ("010.00","10.00"),
    ])
def test_deve_criar_um_valor_corretamente(value,formated):

    amount = Decimal(value)
    assert Amount.validate(amount) == Decimal(formated)

# Restrição de Valor Negativo ao criar
@pytest.mark.parametrize("value, error, error_msg", [
    ("-010.00", InvalidAmount, "O valor deve ser positivo"),
    ("0", InvalidAmount, "O valor deve ser positivo")
    ])
def test_deve_lancar_erro_ao_criar_valor_negativo(value, error, error_msg):

    with pytest.raises(error, match=error_msg):
        Amount.validate(Decimal(value))
