from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.adapters.repositories.sqlalchemy_player_repository import (
    SqlAlchemyPlayerRepository,
)
from app.adapters.repositories.sqlalchemy_credential_repository import (
    SqlAlchemyCredentialRepository,
)


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def __aenter__(self):
        self._session = self._session_factory()
        self.players = SqlAlchemyPlayerRepository(self._session)
        self.credentials = SqlAlchemyCredentialRepository(self._session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type is not None:
            await self._session.rollback()
        await self._session.close()

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
