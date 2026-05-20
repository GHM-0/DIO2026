# src/infrastructure/security/security.py
import time
from typing import Annotated, Union
from uuid import uuid4

import jwt
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, ConfigDict

from infrastructure.config import settings


SECRET = settings.SECRET_KEY  #.replace('"', '').replace("'", "")
ALGORITHM = settings.ALGORITHM #.replace('"', '').replace("'", "")


class AccessToken(BaseModel):
    """Modelo para as claims padrão do JWT conforme a RFC 7519."""
    model_config = ConfigDict(coerce_numbers_to_str=False)
    
    iss: str
    sub: Union[int, str]
    aud: str
    exp: float
    iat: float
    nbf: float
    jti: str


class JWTToken(BaseModel):
    """Representa a resposta enviada ao cliente (o token em si)."""
    access_token: str
    token_type: str = "Bearer"

# Placebo, qualquer user_id int >0 será válidado
def sign_jwt(user_id: int) -> JWTToken:
    """
    Gera um token assinado para um usuário específico.
    Valida se o user_id é um inteiro positivo antes de proceder.
    """
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError("O user_id deve ser um inteiro positivo e não nulo.")

    now = time.time()
    payload = {
        "iss": "desafio-bank.com.br",  # Identifica quem emitiu o token
        "sub": str(user_id),           # Identificador do usuário (sempre string no JWT)
        "aud": "desafio-bank",         # Define para qual aplicação este token é destinado
        "exp": now + (60 * 30),        # Tempo de expiração (Unix timestamp)
        "iat": now,                    # Momento da emissão
        "nbf": now,                    # Token não é válido antes deste momento
        "jti": uuid4().hex,            # ID único do token para prevenção de ataques de reuso
    }

    token = jwt.encode(payload, SECRET, algorithm=ALGORITHM)
    return JWTToken(access_token=token)


async def decode_jwt(token: str) -> AccessToken:
    """
    Realiza a decodificação e validação criptográfica do token.
    A biblioteca PyJWT valida automaticamente 'exp', 'nbf' e 'aud'.
    """
    try:
        decoded_token = jwt.decode(
            token, 
            SECRET, 
            audience="desafio-bank", 
            algorithms=[ALGORITHM],
            options={"verify_exp": True} 
        )
        return AccessToken(**decoded_token)
    except (jwt.PyJWTError, ValueError):
        # Unifica falhas de assinatura, expiração ou audiência em 401 Unauthorized
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )


class JWTBearer(HTTPBearer):
    """Middleware de segurança para extração de tokens do cabeçalho Authorization."""
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request) -> AccessToken:
        authorization = request.headers.get("Authorization", "")
        scheme, _, credentials = authorization.partition(" ")

        if credentials:
            if not scheme == "Bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication scheme.",
                )

            # Delega a validação; se inválido, interrompe a requisição aqui
            return await decode_jwt(credentials)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization code.",
            )


async def get_current_user(
    token: Annotated[AccessToken, Depends(JWTBearer())],
) -> dict[str, int]:
    """Injeta o ID do usuário baseado no token validado."""
    return {"user_id": int(token.sub)}


def login_required(current_user: Annotated[dict[str, int], Depends(get_current_user)]):
    """
    Garante que o endpoint exija autenticação.
    A verificação 'if not current_user' é omitida pois o JWTBearer 
    já garante a existência de um usuário válido.
    """
    return current_user
