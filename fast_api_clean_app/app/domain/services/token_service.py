from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class TokenPair:
    """Пара токенов, выдаваемая клиенту после успешной аутентификации"""
    access_token: str
    refresh_token: str
    expires_in: int # секунды до истечения access-токена
    token_type: str = "Bearer"


class TokenService(Protocol):
    """
    Доменный интерфейс выпуска токенов
    """

    async def issue_pair(self, player_id: UUID) -> TokenPair:
        ...

    async def revoke_refresh(self, refresh_token: str) -> None:
        ...
