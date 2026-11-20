from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from app.domain.repositories.player_repository import PlayerRepository
    from app.domain.repositories.credential_repository import CredentialRepository


class UnitOfWork(Protocol):
    players: "PlayerRepository"
    credentials: "CredentialRepository"

    async def __aenter__(self) -> "UnitOfWork": ...
    async def __aexit__(self, exc_type, exc, tb) -> None: ...
    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...
