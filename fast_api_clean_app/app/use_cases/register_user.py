from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from app.domain.entities.credential import Credential
from app.domain.entities.player import Player
from app.domain.exceptions import EmailAlreadyTakenError
from app.domain.repositories.unit_of_work import UnitOfWork
from app.domain.services.password_hasher import PasswordHasher
from app.domain.services.password_policy import PasswordPolicy
from app.domain.services.token_service import TokenPair, TokenService
from app.domain.value_objects.email import Email


@dataclass(frozen=True)
class RegisterUserCommand:
    """Входные данные сценария. Изолирует Use Case от формата HTTP-запроса"""
    email: str
    password: str
    display_name: str


@dataclass(frozen=True)
class RegisterUserResult:
    player_id: str
    tokens: TokenPair


class RegisterUserUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        hasher: PasswordHasher,
        token_service: TokenService,
        password_policy: PasswordPolicy | None = None,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.token_service = token_service
        self.password_policy = password_policy or PasswordPolicy()

    async def execute(self, command: RegisterUserCommand) -> RegisterUserResult:
        # Валидация формата email (value object бросит InvalidEmailError)
        email = Email(command.email)

        # Проверка сложности пароля (бросит WeakPasswordError)
        self.password_policy.validate(command.password)

        async with self.uow:
            # Проверка уникальности email
            if await self.uow.players.get_by_email(email.value) is not None:
                raise EmailAlreadyTakenError(email.value)

            # Хеширование
            password_hash = self.hasher.hash(command.password)

            # Создание агрегата
            player = Player.create(
                display_name=command.display_name,
                email=email.value,
            )
            credential = Credential.create_with_password(
                player_id=player.id,
                password_hash=password_hash,
            )

            # Сохранение
            await self.uow.players.save(player)
            await self.uow.credentials.save(credential)

            # Токены выпускаются после commit, чтобы при ошибке транзакции клиент не получил "висячие" токены.

            try:
                await self.uow.commit()
            except IntegrityError as exc:
                await self.uow.rollback()
                raise EmailAlreadyTakenError(email.value) from exc

            tokens = await self.token_service.issue_pair(player.id)

            return RegisterUserResult(player_id=str(player.id), tokens=tokens)
