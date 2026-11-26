import hashlib
import itsdangerous
from datetime import datetime, timezone
from uuid import UUID

from app.adapters.controllers.schemas import (
    RegisterRequest, LoginRequest, RefreshRequest,
)
from app.adapters.controllers.dependencies import (
    get_register_use_case,
    get_login_use_case,
    get_login_with_steam_use_case,
    get_link_platform_use_case,
    get_unlink_platform_use_case,
    get_steam_adapter,
    get_link_steam_adapter,
    get_uow,
)
from app.adapters.repositories.sqlalchemy_uow import SqlAlchemyUnitOfWork

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Request
from fastapi.responses import JSONResponse, RedirectResponse

from app.use_cases.register_user import RegisterUserUseCase, RegisterUserCommand
from app.use_cases.link_platform import LinkPlatformUseCase
from app.use_cases.unlink_platform import UnlinkPlatformUseCase
from app.use_cases.authenticate_with_password import (
    AuthenticateWithPasswordUseCase, AuthenticateWithPasswordCommand,
)

from app.adapters.controllers.auth_dependencies import get_current_player
from app.adapters.services.steam_openid import SteamOpenIDAdapter
from app.use_cases.login_with_steam import LoginWithSteamCommand, LoginWithSteamUseCase

from app.domain.entities.player import Player
from app.domain.value_objects.platform_type import PlatformType

from app.domain.exceptions import (
    EmailAlreadyTakenError, InvalidCredentialsError,
    PlayerInactiveError, WeakPasswordError,
)

from app.config import Settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = Settings()
_serializer = itsdangerous.URLSafeTimedSerializer(settings.jwt_secret)

# --- Password ---

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    body: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_use_case),
):
    try:
        result = await use_case.execute(
            RegisterUserCommand(body.email, body.password, body.display_name)
        )
    except EmailAlreadyTakenError as exc:
        raise HTTPException(status.HTTP_409_CONFLICT, exc.message)
    except WeakPasswordError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, exc.message)
    return {
        "player_id": result.player_id,
        "access_token": result.tokens.access_token,
        "refresh_token": result.tokens.refresh_token,
        "token_type": result.tokens.token_type,
        "expires_in": result.tokens.expires_in,
    }


@router.post("/login")
async def login(
    body: LoginRequest,
    use_case: AuthenticateWithPasswordUseCase = Depends(get_login_use_case),
):
    try:
        result = await use_case.execute(
            AuthenticateWithPasswordCommand(body.email, body.password)
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, exc.message)
    except PlayerInactiveError as exc:
        raise HTTPException(status.HTTP_403_FORBIDDEN, exc.message)
    return {
        "player_id": result.player_id,
        "access_token": result.tokens.access_token,
        "refresh_token": result.tokens.refresh_token,
        "token_type": result.tokens.token_type,
        "expires_in": result.tokens.expires_in,
    }

# --- About player ---

@router.get("/me")
async def me(player: Player = Depends(get_current_player)):
    return {
        "id": str(player.id),
        "email": player.email,
        "display_name": player.display_name,
        "status": player.status.value,
        "created_at": player.created_at.isoformat(),
    }

@router.get("/me/platforms")
async def my_platforms(player: Player = Depends(get_current_player)):
    return [
        {"platform": l.platform.value, "platform_user_id": l.platform_user_id}
        for l in player.platform_links
    ]

@router.delete("/me/platforms/{platform}")
async def unlink(
    platform: str,
    player: Player = Depends(get_current_player),
    use_case: UnlinkPlatformUseCase = Depends(get_unlink_platform_use_case),
):
    platform_type = PlatformType.from_string(platform)
    await use_case.execute(player.id, platform_type)
    return {"status": "unlinked"}


# --- Steam --

@router.get("/steam/login")
async def steam_login(
    adapter: SteamOpenIDAdapter = Depends(get_steam_adapter),
):
    return RedirectResponse(adapter.get_redirect_url())

@router.get("/steam/callback")
async def steam_callback(
    request: Request,
    adapter: SteamOpenIDAdapter = Depends(get_steam_adapter),  # ← DI
    use_case: LoginWithSteamUseCase = Depends(get_login_with_steam_use_case),
):
    steam_id = adapter.validate_and_get_steam_id(request.query_params)
    if not steam_id:
        raise HTTPException(status_code=403, detail="Failed to authenticate with Steam")

    result = await use_case.execute(LoginWithSteamCommand(steam_id=steam_id))
    return {
        "player_id": result.player_id,
        "access_token": result.tokens.access_token,
        "refresh_token": result.tokens.refresh_token,
        "token_type": result.tokens.token_type,
        "expires_in": result.tokens.expires_in,
    }

@router.get("/steam/link")
async def steam_link_initiate(
    player: Player = Depends(get_current_player),
    adapter: SteamOpenIDAdapter = Depends(get_link_steam_adapter),
):
    state = _serializer.dumps(str(player.id))
    response = RedirectResponse(adapter.get_redirect_url())
    response.set_cookie("steam_link_state", state, httponly=True, max_age=300)
    return response

@router.get("/steam/link/callback")
async def steam_link_callback(
    request: Request,
    adapter: SteamOpenIDAdapter = Depends(get_link_steam_adapter),
    use_case: LinkPlatformUseCase = Depends(get_link_platform_use_case),
):
    state = request.cookies.get("steam_link_state")
    if not state:
        raise HTTPException(400, "Missing link state")
    try:
        player_id = UUID(_serializer.loads(state, max_age=300))
    except Exception:
        raise HTTPException(400, "Invalid or expired state")

    steam_id = adapter.validate_and_get_steam_id(request.query_params)
    if not steam_id:
        raise HTTPException(403, "Steam auth failed")

    await use_case.execute(player_id, PlatformType.STEAM, steam_id)
    return JSONResponse({"status": "linked", "steam_id": steam_id})

# --- Refresh tokens ---

@router.post("/refresh")
async def refresh_tokens(
    body: RefreshRequest,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    token_hash = hashlib.sha256(body.refresh_token.encode()).hexdigest()
    async with uow:
        record = await uow.refresh_tokens.get_by_hash(token_hash)

        if record is None:
            raise HTTPException(401, "Invalid refresh token")

        # Повторное использование: отзываем всю family
        if record.used:
            await uow.refresh_tokens.revoke_family(record.family_id)
            await uow.commit()
            raise HTTPException(401, "Refresh token reuse detected — all sessions revoked")

        # Просрочен
        if record.expires_at < datetime.now(timezone.utc):
            raise HTTPException(401, "Refresh token expired")

        # Помечаем использованным
        record.used = True
        await uow.refresh_tokens.save(record)

        # Выдаём новую пару в той же family
        tokens = await uow.token_service.issue_pair(
            record.player_id, family_id=record.family_id
        )
        await uow.commit()

        return {
            "access_token": tokens.access_token,
            "refresh_token": tokens.refresh_token,
            "token_type": tokens.token_type,
            "expires_in": tokens.expires_in,
        }

@router.post("/logout")
async def logout(
    body: RefreshRequest,
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
):
    async with uow:
        await uow.token_service.revoke_refresh(body.refresh_token)
        await uow.commit()
    return {"status": "logged out"}
