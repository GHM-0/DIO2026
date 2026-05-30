import pytest
import pytest_asyncio
from fastapi import status
from application.dto.account_dto import AccountResponse

@pytest_asyncio.fixture(scope="function", autouse=True)
async def clean_database(truncate_table):
    """Garante que as tabelas de contas e transações estejam vazias para cada teste."""
    await truncate_table("transactions")
    await truncate_table("accounts")

async def test_deve_criar_criar_uma_conta(api_client, authenticated_headers):
    """
    Deve criar uma nova conta com sucesso e retornar o status 201.
    """
    user_id = 1
    headers = authenticated_headers(user_id)
    request_body = {
        "user_id": user_id,
        "balance": "100.00"
    }

    response = api_client.post("/accounts/", json=request_body, headers=headers)

    assert response.status_code == status.HTTP_201_CREATED

    response_data = response.json()
    assert "id" in response_data
    assert response_data["user_id"] == user_id
    assert response_data["balance"] == request_body["balance"]
    assert "created_at" in response_data

    AccountResponse.model_validate(response_data)

@pytest.mark.parametrize("user_id,balance",[
    (1,"-1"),
    (1,None),
])
async def test_nao_deve_criar_criar_uma_conta_com_atributos_invalido(api_client, authenticated_headers,user_id,balance):
    """
    Deve Falhar ao criar uma nova conta com atributos inválidos e retornar o status 422.
    """
    headers = authenticated_headers(user_id)
    request_body = {
        "user_id": user_id,
        "balance": balance
    }

    response = api_client.post("/accounts/", json=request_body, headers=headers)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

async def test_deve_recuperar_extrato_de_conta_sem_transacoes(api_client, authenticated_headers):
    """
    Deve criar uma conta, adicionar algumas transações e recuperar o extrato dessa conta.
    """
    user_id = 1
    headers = authenticated_headers(user_id)
    request_body = {
        "user_id": user_id,
        "balance": "100.00"
    }

    response_created = api_client.post("/accounts/", json=request_body, headers=headers)
    assert response_created.status_code == status.HTTP_201_CREATED
    created_account_data = response_created.json()
    account_id = created_account_data["id"]

    limit = 10
    skip = 0
    response_statement = api_client.get(
        f"/accounts/{account_id}/transactions?limit={limit}&skip={skip}",
        headers=headers
    )

    assert response_statement.status_code == status.HTTP_200_OK

    statement_data = response_statement.json()

    assert "account" in statement_data
    assert statement_data["account"]["id"] == account_id
    assert statement_data["account"]["user_id"] == user_id

    assert "transactions" in statement_data
    assert isinstance(statement_data["transactions"], list)