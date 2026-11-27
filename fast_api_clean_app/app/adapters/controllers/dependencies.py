from fastapi import Depends
from fastapi_steam import SteamAuth

from app.adapters.repositories.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.adapters.services.bcrypt_password_hasher import BcryptPasswordHasher
from app.infrastructure.database import async_session_factory
from app.config import Settings
from app.use_cases.register_user import RegisterUserUseCase
from app.use_cases.link_platform import LinkPlatformUseCase
from app.use_cases.unlink_platform import UnlinkPlatformUseCase
from app.use_cases.authenticate_with_password import AuthenticateWithPasswordUseCase
from app.use_cases.login_with_steam import LoginWithSteamUseCase
from app.use_cases.game_state import (
    GetGameStateUseCase, UpdateGameStateUseCase, IncrementCounterUseCase,
)
from app.config import settings

_hasher = BcryptPasswordHasher()

# --- Database ---
def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(async_session_factory)


# --- Адаптеры ---

# --- Steam ---
_steam_auth_login = SteamAuth(
    api_key="",
    redirect_uri=settings.steam_return_url,
)

_steam_auth_link = SteamAuth(
    api_key=settings.steam_api_key,
    redirect_uri="http://localhost:8000/auth/steam/link/callback",
)

def get_steam_auth_login() -> SteamAuth:
    return _steam_auth_login

def get_steam_auth_link() -> SteamAuth:
    return _steam_auth_link


# --- Use cases ---
def get_register_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return RegisterUserUseCase(uow, _hasher)


def get_login_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return AuthenticateWithPasswordUseCase(uow, _hasher)


def get_login_with_steam_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return LoginWithSteamUseCase(uow)


def get_link_platform_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return LinkPlatformUseCase(uow)


def get_unlink_platform_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return UnlinkPlatformUseCase(uow)


def get_game_state_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return GetGameStateUseCase(uow)

def get_update_game_state_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return UpdateGameStateUseCase(uow)

def get_increment_counter_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return IncrementCounterUseCase(uow)
