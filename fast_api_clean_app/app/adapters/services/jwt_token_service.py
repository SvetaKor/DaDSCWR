from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

import jwt

from app.config import Settings
from app.domain.services.token_service import TokenPair, TokenService


class JWTTokenService(TokenService):
    def __init__(self, settings: Settings) -> None:
        self._secret = settings.jwt_secret
        self._access_ttl = settings.jwt_access_ttl_sec
        self._refresh_ttl = settings.jwt_refresh_ttl_sec
        self._algorithm = "HS256"

    async def issue_pair(self, player_id: UUID) -> TokenPair:
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

        return TokenPair(
            access_token=access,
            refresh_token=refresh,
            expires_in=self._access_ttl,
        )

    async def revoke_refresh(self, refresh_token: str) -> None:
        # TODO: когда появится таблица refresh_tokens — здесь её пометить revoked
        return None
