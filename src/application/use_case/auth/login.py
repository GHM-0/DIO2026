from application.dto.login_dto import LoginRequest, LoginResponse
from infrastructure.security.security import sign_jwt

class LoginUseCase:
    """
    Orquestra o processo de autenticação e geração de token.
    Em um cenário real, validaria a existência do usuário e senha.
    """

    async def execute(self, request: LoginRequest) -> LoginResponse:

        token_data = sign_jwt(user_id=request.user_id)

        return LoginResponse(
            access_token=token_data.access_token
        )
