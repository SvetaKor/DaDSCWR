from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.domain.exceptions import PlayerNotFoundError
from app.domain.repositories.unit_of_work import UnitOfWork


@dataclass(frozen=True)
class GameStateResult:
    data: dict[str, Any]


class GetGameStateUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, player_id: UUID) -> GameStateResult:
        async with self.uow:
            player = await self.uow.players.get_by_id(player_id)
            if player is None:
                raise PlayerNotFoundError(player_id)
            return GameStateResult(data=dict(player.game_state))


class UpdateGameStateUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, player_id: UUID, data: dict[str, Any]
    ) -> GameStateResult:
        async with self.uow:
            player = await self.uow.players.get_by_id(player_id)
            if player is None:
                raise PlayerNotFoundError(player_id)
            player.update_game_state(data)
            await self.uow.players.save(player)
            await self.uow.commit()
            return GameStateResult(data=dict(player.game_state))


class IncrementCounterUseCase:
    """Удобный частный случай для кликера и подобных счётчиков."""
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(
        self, player_id: UUID, key: str, delta: int = 1
    ) -> GameStateResult:
        async with self.uow:
            player = await self.uow.players.get_by_id(player_id)
            if player is None:
                raise PlayerNotFoundError(player_id)
            player.increment_counter(key, delta)
            await self.uow.players.save(player)
            await self.uow.commit()
            return GameStateResult(data=dict(player.game_state))
