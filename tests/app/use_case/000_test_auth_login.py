import pytest
from fastapi.testclient import TestClient
from main import app

@pytest.fixture(scope="module")
def client():
    """Retorna um TestClient para o FastAPI, garantindo isolamento de contexto."""
    return TestClient(app)

def test_login_success(client):
    """Garante que um usuário pode obter um token com um user_id válido."""
    payload = {"user_id": 1}
    
    # Execução
    response = client.post("/auth/login", json=payload)
    
    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert isinstance(data["access_token"], str)
    assert len(data["access_token"]) > 0


def test_login_invalid_payload(client):
    """Garante que o FastAPI valida o tipo de dado do user_id."""
    payload = {"user_id": "not-a-number"}
    
    response = client.post("/auth/login", json=payload)

    assert response.status_code == 422
