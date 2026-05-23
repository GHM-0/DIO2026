from datetime import datetime
from decimal import Decimal
import pytest
from pydantic import ValidationError

from application.dto.transaction_dto import (
    CreateTransactionRequest,
    TransactionResponse,
)
from core.domain.value_object.transaction_type import TransactionType

@pytest.mark.parametrize("orig,dest, transaction_type, amount", [
    (12,11, TransactionType.CREDIT, Decimal("12.30")),
    (45,678, TransactionType.DEBIT, Decimal("1200.00"))
])
def test_deve_criar_uma_transacao_valida(orig: int,dest:int, transaction_type: TransactionType, amount: Decimal):
    transaction = CreateTransactionRequest(account_orig_id=orig,account_dest_id=dest, type=transaction_type, amount=amount)

    assert isinstance(transaction, CreateTransactionRequest)
    assert transaction.account_orig_id == orig
    assert transaction.account_dest_id == dest
    assert transaction.type == transaction_type
    assert transaction.amount == amount


@pytest.mark.parametrize("orig,dest, transaction_type, amount", [
    (0, 1,TransactionType.CREDIT, Decimal("10.00")),   # account_orig_id inválido (gt=0)
    (1, 1,TransactionType.CREDIT, Decimal("-5.00")),  # amount inválido (ge=0)
    (None, 1,TransactionType.CREDIT, Decimal("10.00")), # account_orig_id nulo
])
def test_deve_falhar_ao_criar_uma_transacao_com_dados_invalidos(orig,dest, transaction_type, amount):
    with pytest.raises(ValidationError):
        CreateTransactionRequest(account_orig_id=orig, account_dest_id=dest, type=transaction_type, amount=amount)

@pytest.mark.parametrize("id, account_orig_id, transaction_type, amount, timestamp", [
    (12, 134, TransactionType.DEBIT, Decimal("1230.00"), datetime.now()),
])
def test_deve_retornar_uma_transacao_valida(id: int, account_orig_id: int, transaction_type: TransactionType, amount: Decimal, timestamp: datetime):
    transaction = TransactionResponse(id=id, account_orig_id=account_orig_id, type=transaction_type, amount=amount, timestamp=timestamp)
    assert isinstance(transaction, TransactionResponse)
    assert transaction.id == id
    assert transaction.timestamp == timestamp
    assert transaction.account_orig_id == account_orig_id
    assert transaction.type == transaction_type
    assert transaction.amount == amount

@pytest.mark.parametrize("id, account_orig_id, transaction_type, amount, timestamp", [
    (None, 134, TransactionType.DEBIT, Decimal("1230.00"), datetime.now()),
    (12, None, TransactionType.DEBIT, Decimal("1230.00"), datetime.now()),
    (12, 134, "", Decimal("1230.00"), datetime.now()),
    (12, 134, None, Decimal("1230.00"), datetime.now()),
    (12, 134, TransactionType.DEBIT, Decimal("-11.00"), datetime.now()),
    (12, 134, TransactionType.DEBIT, Decimal("1230.00"), None),
])
def test_deve_falhar_ao_retornar_uma_transacao_invalida(id, account_orig_id, transaction_type, amount, timestamp):
    with pytest.raises(ValidationError):
        TransactionResponse(id=id, account_orig_id=account_orig_id, type=transaction_type, amount=amount, timestamp=timestamp)