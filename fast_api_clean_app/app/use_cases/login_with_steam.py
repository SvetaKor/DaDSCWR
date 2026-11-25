from dataclasses import dataclass

from app.domain.entities.player import Player
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.services.token_service import TokenPair
from app.domain.value_objects.platform_type import PlatformType


@dataclass(frozen=True)
class LoginWithSteamCommand:
    steam_id: str
    display_name: str | None = None  # опционально, чтобы задать имя


@dataclass(frozen=True)
class LoginWithSteamResult:
    player_id: str
    tokens: TokenPair


class LoginWithSteamUseCase:
    def __init__(self, uow: UnitOfWork) -> None:
        self.uow = uow

    async def execute(self, command: LoginWithSteamCommand) -> LoginWithSteamResult:
        async with self.uow:
            player = await self.uow.players.get_by_platform(
                PlatformType.STEAM, command.steam_id
            )

            if player is None:
                # Первый вход: создаём игрока без email и пароля
                display_name = command.display_name or f"Player_{command.steam_id[:8]}"
                player = Player.create(display_name=display_name, email=None)
                player.link_platform(PlatformType.STEAM, command.steam_id)
                await self.uow.players.save(player)
            else:
                # Повторный вход: проверяем, что аккаунт активен
                player.ensure_can_authenticate()

            tokens = await self.uow.token_service.issue_pair(player.id)
            await self.uow.commit()

            return LoginWithSteamResult(player_id=str(player.id), tokens=tokens)
