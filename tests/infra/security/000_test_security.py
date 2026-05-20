import pytest
from fastapi import HTTPException
from infrastructure.security.security import sign_jwt, decode_jwt, JWTToken, AccessToken


@pytest.mark.asyncio
async def test_deve_gerar_token_valido():
    user_id = 1
    token_obj = sign_jwt(user_id)

    assert isinstance(token_obj, JWTToken), "Deve retornar uma instância de JWTToken"
    assert token_obj.access_token is not None
    assert len(token_obj.access_token.split(".")) == 3


@pytest.mark.asyncio
async def test_deve_validar_um_token_valido():
    user_id = 1
    token_obj = sign_jwt(user_id)

    payload = await decode_jwt(token_obj.access_token)

    assert isinstance(payload, AccessToken)
    assert payload.sub == str(user_id)
    assert payload.aud == "desafio-bank"


@pytest.mark.asyncio
@pytest.mark.parametrize("user_id", [None, "", 0, -1])
async def test_deve_falhar_ao_criar_token_com_dados_invalidos(user_id):
    with pytest.raises(ValueError) as e:
        sign_jwt(user_id)
    
    assert "O user_id deve ser um inteiro positivo e não nulo." in str(e.value)

@pytest.mark.asyncio
async def test_deve_falhar_ao_validar_token_invalido():
    token_invalido = "header.payload.signature_errada"
    with pytest.raises(HTTPException) as e:
        await decode_jwt(token_invalido)
    assert e.value.status_code == 401
