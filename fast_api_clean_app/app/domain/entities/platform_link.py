from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from app.domain.value_objects.platform_type import PlatformType


@dataclass
class PlatformLink:
    """
    Связь игрового аккаунта с конкретной платформой.
    
    Инварианты:
      - platform_user_id не может быть пустым;
      - пара (platform, platform_user_id) уникальна в системе (проверяется на уровне Use Case + UNIQUE constraint в БД);
      - metadata - произвольные JSON-совместимые данные о платформенном профиле (ник, аватар, дата регистрации на платформе и т.п.).
    """
    id: UUID
    player_id: UUID
    platform: PlatformType
    platform_user_id: str
    linked_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(
        cls,
        player_id: UUID,
        platform: PlatformType,
        platform_user_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> "PlatformLink":
        if not platform_user_id or not platform_user_id.strip():
            raise ValueError("platform_user_id cannot be empty")
        if not isinstance(platform, PlatformType):
            raise ValueError("platform must be a PlatformType")

        return cls(
            id=uuid4(),
            player_id=player_id,
            platform=platform,
            platform_user_id=platform_user_id.strip(),
            linked_at=datetime.now(timezone.utc),
            metadata=dict(metadata or {}),
        )

    @property
    def natural_key(self) -> tuple[PlatformType, str]:
        """
        Естественный ключ связи. Используется в Use Case для проверки, не привязан ли этот платформенный аккаунт к другому игроку
        """
        return (self.platform, self.platform_user_id)

    def update_metadata(self, new_metadata: dict[str, Any]) -> None:
        """
        Мягкое обновление метаданных: не перезаписываем ключи, которых нет в new_metadata
        """
        self.metadata.update(new_metadata)

    def __eq__(self, other: object) -> bool:
        # Для сущностей равенство определяется идентификатором, а не полями
        if not isinstance(other, PlatformLink):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)
