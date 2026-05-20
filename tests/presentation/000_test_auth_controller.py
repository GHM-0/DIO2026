import pytest
from fastapi import status

@pytest.mark.parametrize("payload",[
    ({"user_id": "1"}),
    ({"user_id": 1}),
    ])
def test_deve_retornar_um_token_valido_para_dados_validos(api_client,payload):
    """
    Garante que o login retorne um token JWT quando as credenciais (user_id) são válidas.
    """
    # Arrange
    payload = {"user_id": 1}

    # Act
    response = api_client.post("/auth/login", json=payload)

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()
    assert isinstance(response.json()["access_token"], str)

@pytest.mark.parametrize("payload",[
    ({"user_id": "invalid_id"}),
    ({"user_id": -1}),
    ({"user_id": "-1"}),
    ({"user_id": ""}),
    ({"user_id": ''}),
    ({"user_id": "0"}),
    ({"user_id": 0}),
    ({})])
def test_deve_retornar_422_ao_criara_token_com_dados_invalido(api_client,payload):

    """
    Garante que o endpoint exija o corpo da requisição.
    """
    # Act
    response = api_client.post("/auth/login", json=payload)

    # Assert
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
