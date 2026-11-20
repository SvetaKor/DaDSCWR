from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import Settings
from app.domain.entities.player import Player
from app.domain.exceptions import PlayerNotFoundError
from app.adapters.controllers.dependencies import get_uow
from app.adapters.repositories.sqlalchemy_uow import SqlAlchemyUnitOfWork

settings = Settings()
_bearer = HTTPBearer(auto_error=False)


async def get_current_player(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> Player:
    if credentials is None:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Missing Authorization header"
        )
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=["HS256"],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")

    if payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not an access token")

    try:
        player_id = UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token payload")

    async with uow:
        player = await uow.players.get_by_id(player_id)
    if player is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Player not found")
    return player
