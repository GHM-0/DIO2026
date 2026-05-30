# tests.app.dto.001_test_account_dto.py
import pytest
from decimal import Decimal
from datetime import datetime
from pydantic import ValidationError

from application.dto.account_dto import (
    CreateAccountRequest, 
    AccountResponse, 
    AccountUpdateRequest,
)

@pytest.mark.parametrize("user_id, balance", [
    (999, Decimal("-45.00")),
    (None, Decimal("20.00")),
    (0, Decimal("10.00")),
    (-1, Decimal("10.00"))
])
def test_deve_falhar_ao_criar_create_account_request_com_atributos_invalidos(user_id, balance):
    with pytest.raises(ValidationError):
        CreateAccountRequest(user_id=user_id, balance=balance)

@pytest.mark.parametrize("account_id, user_id, balance, created_at", [
    (0, 1, Decimal("100.00"), datetime.now()),
    (1, 1, Decimal("100.00"), "data_invalida"),
])
def test_deve_falhar_ao_criar_account_response_com_atributos_invalidos(account_id, user_id, balance, created_at):
    with pytest.raises(ValidationError):
        AccountResponse(id=account_id, user_id=user_id, balance=balance, created_at=created_at)

def test_deve_criar_account_update_request_com_sucesso():
    balance = Decimal("150.50")
    update_request = AccountUpdateRequest(balance=balance)
    assert update_request.balance == balance