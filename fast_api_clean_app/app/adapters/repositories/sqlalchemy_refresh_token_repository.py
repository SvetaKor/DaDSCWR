from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.adapters.repositories.models import RefreshTokenModel


class SqlAlchemyRefreshTokenRepository(RefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_hash(self, token_hash: str) -> RefreshToken | None:
        stmt = select(RefreshTokenModel).where(
            RefreshTokenModel.token_hash == token_hash
        ).with_for_update() # блокировка от race conditions
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def save(self, token: RefreshToken) -> None:
        model = await self._session.get(RefreshTokenModel, token.id)
        if model is None:
            model = RefreshTokenModel(id=token.id)
            self._session.add(model)
        model.player_id = token.player_id
        model.token_hash = token.token_hash
        model.family_id = token.family_id
        model.used = token.used
        model.revoked = token.revoked
        model.expires_at = token.expires_at
        model.created_at = token.created_at
        await self._session.flush()

    async def revoke_family(self, family_id: UUID) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(RefreshTokenModel.family_id == family_id)
            .values(revoked=True)
        )
        await self._session.flush()

    async def revoke(self, token_id: UUID) -> None:
        model = await self._session.get(RefreshTokenModel, token_id)
        if model is not None:
            model.revoked = True
            await self._session.flush()

    @staticmethod
    def _to_entity(model: RefreshTokenModel) -> RefreshToken:
        return RefreshToken(
            id=model.id,
            player_id=model.player_id,
            token_hash=model.token_hash,
            family_id=model.family_id,
            used=model.used,
            revoked=model.revoked,
            expires_at=model.expires_at,
            created_at=model.created_at,
        )
