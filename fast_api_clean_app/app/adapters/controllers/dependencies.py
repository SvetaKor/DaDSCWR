from fastapi import Depends

from app.adapters.repositories.sqlalchemy_uow import SqlAlchemyUnitOfWork
from app.adapters.services.bcrypt_password_hasher import BcryptPasswordHasher
from app.adapters.services.jwt_token_service import JWTTokenService
from app.infrastructure.database import async_session_factory
from app.config import Settings
from app.use_cases.register_user import RegisterUserUseCase
from app.use_cases.authenticate_with_password import AuthenticateWithPasswordUseCase


settings = Settings()

_hasher = BcryptPasswordHasher()
_token_service = JWTTokenService(settings)


def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(async_session_factory)


def get_register_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return RegisterUserUseCase(uow, _hasher, _token_service)


def get_login_use_case(uow: SqlAlchemyUnitOfWork = Depends(get_uow)):
    return AuthenticateWithPasswordUseCase(uow, _hasher, _token_service)
