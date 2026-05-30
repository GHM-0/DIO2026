from decimal import Decimal

import pytest
import pytest_asyncio
from fastapi import status

from core.domain.value_object.transaction_type import TransactionType


@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database(truncate_table):
    """Garante que as tabelas de contas e transações estejam vazias para cada teste."""
    await truncate_table("transactions")
    await truncate_table("accounts")

@pytest.mark.parametrize("user_1,balance1,user_2,balance2,valor",[
    (1,200,2,0,50),
    (1,500,2,100,400)
])
def test_deve_criar_a_transacao_para_entre_contas(api_client, authenticated_headers,user_1,balance1,user_2,balance2,valor):

    # Arrange
    headers_user1 = authenticated_headers(user_1)
    create_account1 = {
        "user_id": user_1,
        "balance": balance1
    }

    response_create1 = api_client.post("/accounts/", json=create_account1, headers=headers_user1)

    assert response_create1.status_code == status.HTTP_201_CREATED

    headers_user2 = authenticated_headers(user_2)
    create_account2 = {
        "user_id": user_2,
        "balance": balance2
    }

    response_create2 = api_client.post("/accounts/", json=create_account2, headers=headers_user2)

    assert response_create2.status_code == status.HTTP_201_CREATED

    # Criar a Transação
    crete_transaction ={
        "account_orig_id": response_create1.json()["id"],
        "account_dest_id": response_create2.json()["id"],
        "type": TransactionType.TRANSFERENCE.value,
        "amount": valor
    }

    response_transaction = api_client.post("/transactions/",json=crete_transaction,headers=headers_user1)

    assert response_transaction.status_code == status.HTTP_201_CREATED


    limit=10
    skip=0
    response_statement = api_client.get(f"/accounts/{create_account1['user_id']}/transactions?limit={limit}&skip={skip}",headers=headers_user1)

    assert response_statement.status_code == status.HTTP_200_OK

    transaction_response = response_statement.json()

    assert Decimal(transaction_response["account"]["balance"]) == Decimal(str(balance1)) - Decimal(str(valor))

    assert len(transaction_response["transactions"]) > 0, "Nenhuma transação encontrada no extrato."

    transaction_response1 = transaction_response["transactions"][0]

    assert transaction_response1["account_orig_id"] == response_create1.json()["id"]
    assert transaction_response1["account_dest_id"] == response_create2.json()["id"]
    assert transaction_response1["type"] == TransactionType.TRANSFERENCE.value
    assert Decimal(transaction_response1["amount"]) == Decimal(str(valor))
    assert transaction_response1["status"] == "Concluded"
    assert "id" in transaction_response1
    assert "timestamp" in transaction_response1

@pytest.mark.parametrize(
    "exception, "
    "setup_user_1_id, setup_balance_1, "
    "setup_user_2_id, setup_balance_2, "
    "request_orig_id_param, request_dest_id_param, "
    "request_amount, requester_user_id, "
    "expected_error_message_template",
    [
        (
                "Origin account not found",
                None, None,  # Não cria conta para user_1
                2, 0.00,     # Cria conta para user_2
                99999, "account_2_id",  # ID fixo inexistente para origem, placeholder para destino
                10.00, 1,
                "Conta de origem {request_orig_id} não encontrada."
        ),
        (
                "Destination account not found",
                1, 100.00,  # Cria conta para user_1
                None, None,  # Não cria conta para user_2
                "account_1_id", 99998,  # Placeholder para origem, ID fixo inexistente para destino
                10.00, 1,
                "Conta destino {request_dest_id} não encontrada."
        ),
        (
                "Insufficient funds",
                1, 50.00,  # Cria conta para user_1 com saldo baixo
                2, 0.00,  # Cria conta para user_2
                "account_1_id", "account_2_id",  # Placeholders para IDs de contas criadas
                100.00, 1,  # Valor maior que o saldo de user_1
                "Erro ao Criar Transação:saldo insuficiente para saque"
        ),
        (
                "Unauthorized user for origin account",
                1, 100.00,  # Cria conta para user_1
                2, 0.00,  # Cria conta para user_2
                "account_1_id", "account_2_id",  # Placeholders para IDs de contas criadas
                10.00, 3,  # User 3 tenta operar na conta de user 1
                "Usuário não autorizado a operar nesta conta de origem."
        ),
    ]
)
def test_deve_falhar_ao_criar_a_transacao_com_parametros_invalidos(  # Removido 'async' aqui
        api_client, authenticated_headers,
        exception,
        setup_user_1_id, setup_balance_1,
        setup_user_2_id, setup_balance_2,
        request_orig_id_param, request_dest_id_param,
        request_amount, requester_user_id,
        expected_error_message_template
):
    created_account_ids = {}

    if setup_user_1_id is not None:
        headers_user1 = authenticated_headers(setup_user_1_id)
        response_create1 = api_client.post(
            "/accounts/", json={"user_id": setup_user_1_id, "balance": setup_balance_1}, headers=headers_user1
        )
        assert response_create1.status_code == status.HTTP_201_CREATED
        created_account_ids["account_1_id"] = response_create1.json()["id"]

    if setup_user_2_id is not None:
        headers_user2 = authenticated_headers(setup_user_2_id)
        response_create2 = api_client.post(
            "/accounts/", json={"user_id": setup_user_2_id, "balance": setup_balance_2}, headers=headers_user2
        )
        assert response_create2.status_code == status.HTTP_201_CREATED
        created_account_ids["account_2_id"] = response_create2.json()["id"]


    transaction_orig_id = request_orig_id_param
    if isinstance(request_orig_id_param, str) and request_orig_id_param in created_account_ids:
        transaction_orig_id = created_account_ids[request_orig_id_param]

    transaction_dest_id = request_dest_id_param
    if isinstance(request_dest_id_param, str) and request_dest_id_param in created_account_ids:
        transaction_dest_id = created_account_ids[request_dest_id_param]


    crete_transaction = {
        "account_orig_id": transaction_orig_id,
        "account_dest_id": transaction_dest_id,
        "type": TransactionType.TRANSFERENCE.value,
        "amount": request_amount
    }


    error_message_context = {
        "request_orig_id": transaction_orig_id,
        "request_dest_id": transaction_dest_id,
        **created_account_ids
    }
    expected_detail_message = expected_error_message_template.format(**error_message_context)


    headers_for_transaction = authenticated_headers(requester_user_id)
    response_transaction = api_client.post(
        "/transactions/", json=crete_transaction, headers=headers_for_transaction
    )

    # 6. Asserções
    assert response_transaction.status_code == status.HTTP_400_BAD_REQUEST
    response_data = response_transaction.json()
    assert "detail" in response_data
    assert response_data["detail"] == expected_detail_message

# teste a ser corrigido
@pytest.mark.parametrize("user_1,balance1,user_2,balance2,valor",[
    (1,200,2,0,50),
    (1,500,2,100,400)
])
def test_deve_recuperar_extrato_de_conta_com_transacoes(api_client, authenticated_headers,user_1,balance1,user_2,balance2,valor):

    # Arrange
    headers_user1 = authenticated_headers(user_1)
    create_account1 = {
        "user_id": user_1,
        "balance": balance1
    }

    response_create1 = api_client.post("/accounts/", json=create_account1, headers=headers_user1)
    assert response_create1.status_code == status.HTTP_201_CREATED
    account1_id = response_create1.json()["id"]

    headers_user2 = authenticated_headers(user_2)
    create_account2 = {
        "user_id": user_2,
        "balance": balance2
    }

    response_create2 = api_client.post("/accounts/", json=create_account2, headers=headers_user2)
    assert response_create2.status_code == status.HTTP_201_CREATED
    account2_id = response_create2.json()["id"]

    # Criar a Transação
    crete_transaction ={
        "account_orig_id": account1_id,
        "account_dest_id": account2_id,
        "type": TransactionType.TRANSFERENCE.value,
        "amount": valor
    }

    response_transaction = api_client.post("/transactions/",json=crete_transaction,headers=headers_user1)
    assert response_transaction.status_code == status.HTTP_201_CREATED

    # Act - Recuperar extrato de transações da conta de origem
    limit=10
    skip=0
    response_transactions_list = api_client.get(
        f"/transactions/{user_1}?limit={limit}&skip={skip}",
        headers=headers_user1
    )

    # Assert - Verificar a resposta da lista de transações
    assert response_transactions_list.status_code == status.HTTP_200_OK
    transactions_list = response_transactions_list.json()

    assert len(transactions_list) > 0, "Nenhuma transação encontrada no extrato."
    assert isinstance(transactions_list, list)

    # Verificar a primeira transação na lista
    transaction_response1 = transactions_list[0]

    assert transaction_response1["account_orig_id"] == account1_id
    assert transaction_response1["account_dest_id"] == account2_id
    assert transaction_response1["type"] == TransactionType.TRANSFERENCE.value
    assert Decimal(transaction_response1["amount"]) == Decimal(str(valor))
    assert transaction_response1["status"] == "Concluded"
    assert "id" in transaction_response1
    assert "timestamp" in transaction_response1


    response_account_details = api_client.get(
        f"/accounts/{user_1}/transactions?limit={limit}&skip={skip}",
        headers=headers_user1
    )


    assert response_account_details.status_code == status.HTTP_200_OK
    account_details_data = response_account_details.json()
    assert Decimal(account_details_data["account"]["balance"]) == Decimal(str(balance1)) - Decimal(str(valor))

    print(f"{account_details_data}")
    assert "account" in account_details_data
    assert isinstance(account_details_data["account"], dict)
    assert account_details_data["account"]["id"] == account1_id
    assert account_details_data["account"]["user_id"] == user_1
    assert "created_at" in account_details_data["account"]

    assert "transactions" in account_details_data
    assert isinstance(account_details_data["transactions"], list)
    assert len(account_details_data["transactions"]) > 0

    transaction_in_details = account_details_data["transactions"][0]
    assert isinstance(transaction_in_details, dict)
    assert "id" in transaction_in_details
    assert transaction_in_details["account_orig_id"] == account1_id
    assert transaction_in_details["account_dest_id"] == account2_id
    assert transaction_in_details["type"] == TransactionType.TRANSFERENCE.value
    assert Decimal(transaction_in_details["amount"]) == Decimal(str(valor))
    assert "timestamp" in transaction_in_details
    assert transaction_in_details["status"] == "Concluded"
    assert transaction_in_details["message"] is None