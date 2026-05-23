import pytest
import pytest_asyncio
from fastapi import status

from core.domain.value_object.transaction_type import TransactionType

@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_tables(truncate_table):
    """Garante que as tabelas de contas e transações estejam vazias para cada teste."""
    await truncate_table("transactions")
    await truncate_table("accounts")

# Erro 401 Não Autorizado
def test_deve_falhar_ao_acessar_o_route_sem_token(api_client):
    response = api_client.get("/accounts/")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json() == {"detail": "Invalid authorization code."}


def test_deve_falhar_ao_acessar_o_router_com_token_expirado_ou_invalido(api_client):

    headers = {"Authorization": "NO TOKEN"}

    response = api_client.get("/accounts/", headers=headers)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED

    assert response.json() == {"detail": "Invalid authentication scheme."}

# Status 200
@pytest.mark.parametrize("payload", [
    ({"user_id": 1, "balance": 100.0}),
    ({"user_id": 1, "balance": 10.0}),
    ({"user_id": 1, "balance": 1000.0}),
])
def test_deve_criar_uma_nova_conta_com_dados_validos(api_client, payload, authenticated_headers):
    # Arrange
    headers = authenticated_headers(payload["user_id"])
    response = api_client.post("/accounts/", json=payload, headers=headers)

    # Assert
    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["user_id"] == payload["user_id"]
    assert "id" in data
    assert float(data["balance"]) == payload["balance"]

    # Check
    response_get = api_client.get(f"/accounts/", headers=headers)
    assert response_get.status_code == status.HTTP_200_OK
    
    accounts = response_get.json()
    account_ids = [acc["id"] for acc in accounts]
    assert data["id"] in account_ids


@pytest.mark.parametrize("user_id",[
        ({"user_id": 1})
])
def test_deve_listar_todas_as_contas_existentes(api_client, user_id, authenticated_headers):
    # Arrange
    headers = authenticated_headers(user_id["user_id"])
    response = api_client.get("/accounts/", headers=headers)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.parametrize("user_id",[
        ({"user_id":1})
])
@pytest.mark.asyncio
async def test_deve_retornar_o_extrato_de_transacoes_de_uma_conta_valida_sem_transacoes(api_client, user_id, authenticated_headers, db_to_test):
    # Arrange
    user_id_value = user_id["user_id"]
    setup_config = [
        {
            "user_id": user_id_value,
            "balance": 100.0,
            "transactions": [] # Nenhuma transação
        }
    ]
    seeded_data = await db_to_test(setup_config)
    account_id = seeded_data[0]["account"].id
    headers = authenticated_headers(user_id_value)

    # Act
    response = api_client.get(
        f"/transactions/{account_id}", # Rota corrigida
        headers=headers
    )

    # Assert
    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    assert isinstance(data, list)
    assert len(data) == 0 # Espera-se uma lista vazia de transações


@pytest.mark.asyncio
@pytest.mark.parametrize("test_case", [
    {
        "user_id": 1,
        "balance": 1000.0,
        "transactions": [
            {"amount": 200.0, "transaction_type": TransactionType.CREDIT},
            {"amount": 50.0, "transaction_type": TransactionType.DEBIT}
        ]
    }
])
async def test_deve_retornar_o_extrato_de_transacoes_de_uma_conta_valida_com_transacoes(
        api_client,
        db_to_test,
        authenticated_headers,
        test_case
):
    # 1. Arrange: Popula o banco usando a fixture de lote
    seeded_data = await db_to_test([test_case])
    account_persisted = seeded_data[0]["account"]
    
    headers = authenticated_headers(test_case["user_id"])

    # 2. Act: Chama o endpoint correto (/transactions/{id})
    response = api_client.get(
        f"/transactions/{account_persisted.id}",
        headers=headers
    )

    # 3. Assert: Validações lógicas
    assert response.status_code == status.HTTP_200_OK
    
    transactions_list = response.json()

    # O endpoint retorna uma lista de transações conforme o controller atual
    assert isinstance(transactions_list, list)
    assert len(transactions_list) == len(test_case["transactions"])
    assert transactions_list[0]["account_orig_id"] == account_persisted.id

    # Validação de valor (convertendo para float para comparar com o setup)
    assert float(transactions_list[0]["amount"]) == test_case["transactions"][0]["amount"]
    assert transactions_list[0]["transaction_type"] == test_case["transactions"][0]["transaction_type"].value # Comparar o valor do Enum

    assert float(transactions_list[1]["amount"]) == test_case["transactions"][1]["amount"]
    assert transactions_list[1]["transaction_type"] == test_case["transactions"][1]["transaction_type"].value # Comparar o valor do Enum