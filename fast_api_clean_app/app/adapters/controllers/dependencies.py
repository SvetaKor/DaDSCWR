from fastapi import Depends

from app.adapters.repositories.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.adapters.services.bcrypt_password_hasher import BcryptPasswordHasher
from app.adapters.services.jwt_token_service import JWTTokenService
from app.adapters.services.steam_openid import SteamOpenIDAdapter
from app.infrastructure.database import async_session_factory
from app.config import Settings
from app.use_cases.register_user import RegisterUserUseCase
from app.use_cases.link_platform import LinkPlatformUseCase
from app.use_cases.unlink_platform import UnlinkPlatformUseCase
from app.use_cases.authenticate_with_password import AuthenticateWithPasswordUseCase
from app.use_cases.login_with_steam import LoginWithSteamUseCase


settings = Settings()

_hasher = BcryptPasswordHasher()
_token_service = JWTTokenService(settings)


# --- Database ---
def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(async_session_factory)


# --- Адаптеры ---

# Singleton
_steam_adapter = SteamOpenIDAdapter(realm=settings.steam_realm, return_to=settings.steam_return_url)


def get_steam_adapter() -> SteamOpenIDAdapter:
    return _steam_adapter


# --- Use cases ---
def get_register_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return RegisterUserUseCase(uow, _hasher, _token_service)


def get_login_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return AuthenticateWithPasswordUseCase(uow, _hasher, _token_service)


def get_login_with_steam_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return LoginWithSteamUseCase(uow, _token_service)


def get_link_platform_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return LinkPlatformUseCase(uow)


def get_unlink_platform_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return UnlinkPlatformUseCase(uow)
