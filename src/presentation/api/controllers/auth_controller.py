# src/presentation/api/controllers/auth_controller.py
from typing import Annotated
from fastapi import APIRouter, Depends, status

from application.dto.login_dto import LoginRequest, LoginResponse
from application.use_case.auth.login import LoginUseCase

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Provider para o Use Case de Login
def get_login_use_case() -> LoginUseCase:
    return LoginUseCase()

@router.post("/login", response_model=LoginResponse, status_code=status.HTTP_200_OK)
async def login(
    request: LoginRequest,
    use_case: Annotated[LoginUseCase, Depends(get_login_use_case)]
) -> LoginResponse:
    """
    Realiza o login e retorna um token JWT.
    """
    return await use_case.execute(request)
