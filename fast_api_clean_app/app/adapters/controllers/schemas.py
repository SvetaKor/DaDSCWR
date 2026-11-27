from pydantic import BaseModel, EmailStr, Field
from typing import Any


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    display_name: str = Field(min_length=1, max_length=64)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=1)


class GameStateRequest(BaseModel):
    data: dict[str, Any] = Field(..., description="Произвольный JSON - состояние игры")
