from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.credential import Credential, CredentialType
from app.domain.repositories.credential_repository import CredentialRepository
from app.adapters.repositories.models import CredentialModel
from app.adapters.repositories.mappers import (
    to_credential_entity, to_credential_model,
)


class SqlAlchemyCredentialRepository(CredentialRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_player_and_type(
        self, player_id: UUID, cred_type: CredentialType
    ) -> Credential | None:
        stmt = select(CredentialModel).where(
            CredentialModel.player_id == player_id,
            CredentialModel.type == cred_type.value,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return to_credential_entity(model) if model else None

    async def save(self, credential: Credential) -> None:
        existing = await self._session.get(CredentialModel, credential.id)
        model = to_credential_model(credential, existing)
        self._session.add(model)
        await self._session.flush()

    async def delete(self, credential_id: UUID) -> None:
        model = await self._session.get(CredentialModel, credential_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.flush()
