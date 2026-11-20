from uuid import UUID

from app.domain.entities.player import Player
from app.domain.exceptions import PlayerNotFoundError, PlatformNotLinkedError
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.value_objects.platform_type import PlatformType


class UnlinkPlatformUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, player_id: UUID, platform: PlatformType) -> Player:
        async with self.uow:
            player = await self.uow.players.get_by_id(player_id)
            if player is None:
                raise PlayerNotFoundError(player_id)

            if not player.has_platform(platform):
                raise PlatformNotLinkedError(platform)

            player.unlink_platform(platform) # бизнес-правила внутри

            await self.uow.players.save(player)
            await self.uow.commit()
            return player
