from dataclasses import dataclass

from app.domain.entities.credential import CredentialType
from app.domain.exceptions import InvalidCredentialsError
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.services.password_hasher import PasswordHasher
from app.domain.services.token_service import TokenPair
from app.domain.value_objects.email import Email
from app.domain.exceptions import InvalidEmailError

@dataclass(frozen=True)
class AuthenticateWithPasswordCommand:
    email: str
    password: str


@dataclass(frozen=True)
class AuthenticateResult:
    player_id: str
    tokens: TokenPair


# Фиктивный хеш, чтобы выравнивать время ответа при несуществующем email
# Сгенерирован один раз bcryptом для строки-заглушки
_DUMMY_HASH = "$2b$12$v.tN.4KUA.7YBNdpGw3hSeIHlCDWjzKPc32zfdR3zfv7zJGjpwhaa"


class AuthenticateWithPasswordUseCase:
    def __init__(self, uow: UnitOfWork, hasher: PasswordHasher) -> None:
        self.uow = uow
        self.hasher = hasher

    async def execute(self, command) -> AuthenticateResult:
        try:
            email = Email(command.email)
        except InvalidEmailError:
            self.hasher.verify(command.password, _DUMMY_HASH)
            raise InvalidCredentialsError()

        async with self.uow:
            player = await self.uow.players.get_by_email(email.value)
            if player is None:
                self.hasher.verify(command.password, _DUMMY_HASH)
                raise InvalidCredentialsError()

            credential = await self.uow.credentials.get_by_player_and_type(
                player.id, CredentialType.PASSWORD,
            )
            if credential is None or not credential.verify_password(
                command.password, self.hasher,
            ):
                raise InvalidCredentialsError()

            # Статус проверяем после пароля: иначе злоумышленник без пароля сможет узнать, что аккаунт заблокирован
            player.ensure_can_authenticate()

            credential.mark_used()
            await self.uow.credentials.save(credential)

            tokens = await self.uow.token_service.issue_pair(player.id)
            await self.uow.commit()

            return AuthenticateResult(player_id=str(player.id), tokens=tokens)
