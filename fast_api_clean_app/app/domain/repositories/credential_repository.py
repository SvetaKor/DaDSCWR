from typing import Protocol
from uuid import UUID

from app.domain.entities.credential import Credential, CredentialType


class CredentialRepository(Protocol):
    async def get_by_player_and_type(
        self, player_id: UUID, cred_type: CredentialType
    ) -> Credential | None: ...

    async def save(self, credential: Credential) -> None: ...

    async def delete(self, credential_id: UUID) -> None: ...
