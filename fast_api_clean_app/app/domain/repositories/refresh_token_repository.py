from typing import Protocol
from uuid import UUID

from app.domain.entities.refresh_token import RefreshToken


class RefreshTokenRepository(Protocol):
    async def get_by_hash(self, token_hash: str) -> RefreshToken | None: ...

    async def save(self, token: RefreshToken) -> None: ...

    async def revoke_family(self, family_id: UUID) -> None: ...

    async def revoke(self, token_id: UUID) -> None: ...
