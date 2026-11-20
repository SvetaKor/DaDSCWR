from typing import Protocol, runtime_checkable
from uuid import UUID

from app.domain.entities.player import Player
from app.domain.value_objects.platform_type import PlatformType


@runtime_checkable
class PlayerRepository(Protocol):
    """
    Интерфейс репозитория игроков.

    Определяет операции доступа к агрегату Player, необходимые сценариям (Use Cases)
    """

    def get_by_id(self, player_id: UUID) -> Player | None:
        """
        Возвращает игрока по внутреннему ID или None, если не найден
        """
        ...

    def get_by_platform(
        self, platform: PlatformType, platform_user_id: str
    ) -> Player | None:
        """
        Находит игрока по паре (platform, platform_user_id).

        Используется при входе через внешнюю платформу: когда приходит steam_id, нужно понять, какому игроку он принадлежит.

        Возвращает None, если такой связи ещё нет (первый вход)
        """
        ...

    def exists_by_platform(
        self, platform: PlatformType, platform_user_id: str
    ) -> bool:
        """
        Проверяет, привязан ли платформенный аккаунт к какому-либо игроку
        """
        ...

    def get_by_email(self, email: str) -> Player | None:
        """
        Находит игрока по email.

        Используется при входе по email/паролю и при регистрации (проверка, что email ещё не занят)
        """
        ...

    def save(self, player: Player) -> None:
        """
        Сохраняет агрегат Player: создаёт, если его нет, или обновляет
        """
        ...

    def delete(self, player_id: UUID) -> None:
        """
        Каскадно удаляет игрока и все связанные данные
        """
        ...
