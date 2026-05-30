# src.application.dto.login_dto.py

from pydantic import BaseModel,Field

class LoginRequest(BaseModel):
    user_id: int = Field(gt=0)

class LoginResponse(BaseModel):
    access_token: str