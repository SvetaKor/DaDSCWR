from uuid import UUID

from app.domain.entities.player import Player
from app.domain.exceptions import (
    PlayerNotFoundError,
    PlatformAlreadyLinkedToAnotherPlayerError,
)
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.value_objects.platform_type import PlatformType


class LinkPlatformUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self,
        player_id: UUID,
        platform: PlatformType,
        platform_user_id: str,
        metadata: dict | None = None,
    ) -> Player:
        async with self.uow:
            player = await self.uow.players.get_by_id(player_id)
            if player is None:
                raise PlayerNotFoundError(player_id)

            existing = await self.uow.players.get_by_platform(
                platform, platform_user_id,
            )
            if existing is not None and existing.id != player.id:
                raise PlatformAlreadyLinkedToAnotherPlayerError(
                    platform, platform_user_id,
                )

            # Домен сам бросит PlatformAlreadyLinkedError, если у этого игрока платформа уже привязана
            player.link_platform(platform, platform_user_id, metadata=metadata)

            await self.uow.players.save(player)
            await self.uow.commit()
            return player
        