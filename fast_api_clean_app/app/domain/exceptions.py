from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.domain.value_objects.platform_type import PlatformType


# ---------- Базовые ----------

class DomainError(Exception):
    """Базовый класс для всех доменных ошибок"""
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class ValueObjectError(DomainError):
    """Ошибка конструирования value object"""


# ---------- Value objects ----------

class InvalidEmailError(ValueObjectError):
    pass


class InvalidPasswordHashError(ValueObjectError):
    pass


class InvalidPlatformError(ValueObjectError):
    pass


# ---------- Player ----------

class PlayerError(DomainError):
    pass

class PlayerNotFoundError(PlayerError):
    """Игрок с указанным ID не найден"""
    def __init__(self, player_id) -> None:
        self.player_id = player_id
        super().__init__(f"Player with id '{player_id}' not found")


class PlayerInactiveError(PlayerError):
    """Игрок заблокирован/удалён - аутентификация запрещена"""

# ---------- PlatformLink ----------

class PlatformLinkError(DomainError):
    pass

class PlatformAlreadyLinkedError(PlatformLinkError):
    """Эта платформа уже привязана к данному игроку"""
    def __init__(self, platform: "PlatformType") -> None:
        self.platform = platform
        super().__init__(
            f"Platform '{platform.value}' is already linked to this player"
        )


class PlatformNotLinkedError(PlatformLinkError):
    """Платформа не привязана - отвязывать нечего"""
    def __init__(self, platform: "PlatformType") -> None:
        self.platform = platform
        super().__init__(
            f"Platform '{platform.value}' is not linked to this player"
        )


class CannotUnlinkLastAuthMethodError(PlatformLinkError):
    """
    Попытка отвязать последний способ входа при отсутствии пароля.
    Иначе игрок потеряет доступ к аккаунту
    """


class PlatformAlreadyLinkedToAnotherPlayerError(PlatformLinkError):
    """
    Платформенный аккаунт уже привязан к другому игроку
    """
    def __init__(self, platform: "PlatformType", platform_user_id: str) -> None:
        self.platform = platform
        self.platform_user_id = platform_user_id
        super().__init__(
            f"Platform account '{platform.value}:{platform_user_id}' "
            f"is already linked to another player"
        )


# ---------- Credential ----------

class CredentialError(DomainError):
    pass


class InvalidPasswordError(CredentialError):
    """Неверный пароль при аутентификации"""


class WeakPasswordError(CredentialError):
    """Пароль не соответствует политике сложности"""


class EmailAlreadyTakenError(DomainError):
    """Email уже используется другим игроком."""
    def __init__(self, email: str) -> None:
        self.email = email
        super().__init__(f"Email '{email}' is already registered")


class InvalidCredentialsError(DomainError):
    """
    Неверная пара email/пароль.

    Намеренно не уточняем, что именно неверно
    """
    def __init__(self) -> None:
        super().__init__("Invalid email or password")
