from uuid import UUID

from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.entities.player import Player
from app.domain.repositories.player_repository import PlayerRepository
from app.domain.value_objects.platform_type import PlatformType
from app.adapters.repositories.models import PlayerModel, PlatformLinkModel
from app.adapters.repositories.mappers import to_player_entity, to_player_model


class SqlAlchemyPlayerRepository(PlayerRepository):
    """
    Реализация PlayerRepository 
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, player_id: UUID) -> Player | None:
        stmt = (
            select(PlayerModel)
            .where(PlayerModel.id == player_id)
            .options(
                selectinload(PlayerModel.platform_links),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_player_entity(model) if model else None

    async def get_by_platform(
        self, platform: PlatformType, platform_user_id: str
    ) -> Player | None:
        stmt = (
            select(PlayerModel)
            .join(PlayerModel.platform_links)
            .where(
                PlatformLinkModel.platform == platform.value,
                PlatformLinkModel.platform_user_id == platform_user_id,
            )
            .options(
                selectinload(PlayerModel.platform_links),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_player_entity(model) if model else None

    async def exists_by_platform(
        self, platform: PlatformType, platform_user_id: str
    ) -> bool:
        stmt = select(
            exists().where(
                PlatformLinkModel.platform == platform.value,
                PlatformLinkModel.platform_user_id == platform_user_id,
            )
        )
        result = await self._session.execute(stmt)
        return bool(result.scalar())

    async def get_by_email(self, email: str) -> Player | None:
        stmt = (
            select(PlayerModel)
            .where(PlayerModel.email == email)
            .options(
                selectinload(PlayerModel.platform_links),
            )
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_player_entity(model) if model else None

    async def save(self, player: Player) -> None:
        # Пытаемся найти существующую ORM-модель по id
        existing = await self._session.get(PlayerModel, player.id)
        model = to_player_model(player, existing)
        self._session.add(model)
        await self._session.flush()

    async def delete(self, player_id: UUID) -> None:
        model = await self._session.get(PlayerModel, player_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()
