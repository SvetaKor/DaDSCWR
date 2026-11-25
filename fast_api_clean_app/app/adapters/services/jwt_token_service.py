import hashlib
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

from app.config import Settings
from app.domain.entities.refresh_token import RefreshToken
from app.domain.repositories.refresh_token_repository import RefreshTokenRepository
from app.domain.services.token_service import TokenPair, TokenService


class JWTTokenService(TokenService):
    def __init__(
        self,
        settings: Settings,
        refresh_tokens: RefreshTokenRepository,
    ) -> None:
        self._secret = settings.jwt_secret
        self._access_ttl = settings.jwt_access_ttl_sec
        self._refresh_ttl = settings.jwt_refresh_ttl_sec
        self._algorithm = "HS256"
        self._refresh_tokens = refresh_tokens

    def _hash(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    async def issue_pair(
        self,
        player_id: UUID,
        family_id: UUID | None = None,
    ) -> TokenPair:
        now = datetime.now(timezone.utc)

        access_payload = {
            "sub": str(player_id),
            "iat": now,
            "exp": now + timedelta(seconds=self._access_ttl),
            "type": "access",
        }
        access = jwt.encode(access_payload, self._secret, algorithm=self._algorithm)

        refresh_payload = {
            "sub": str(player_id),
            "iat": now,
            "exp": now + timedelta(seconds=self._refresh_ttl),
            "type": "refresh",
            "jti": str(uuid4()),
        }
        refresh = jwt.encode(refresh_payload, self._secret, algorithm=self._algorithm)

        # Сохранение хеша refresh-токена в БД
        token_record = RefreshToken(
            id=uuid4(),
            player_id=player_id,
            token_hash=self._hash(refresh),
            family_id=family_id or uuid4(), # новый логин и новая family
            used=False,
            revoked=False,
            expires_at=now + timedelta(seconds=self._refresh_ttl),
            created_at=now,
        )
        await self._refresh_tokens.save(token_record)

        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=self._access_ttl,
        )

    async def revoke_refresh(self, refresh_token: str) -> None:
        record = await self._refresh_tokens.get_by_hash(self._hash(refresh_token))
        if record is not None:
            await self._refresh_tokens.revoke(record.id)
