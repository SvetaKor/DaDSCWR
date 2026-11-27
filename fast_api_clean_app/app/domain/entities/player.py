from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum
from typing import Any

from app.domain.entities.platform_link import PlatformLink
from app.domain.value_objects.platform_type import PlatformType
from app.domain.exceptions import (
    PlatformAlreadyLinkedError,
    CannotUnlinkLastAuthMethodError,
    PlayerInactiveError,
)


class PlayerStatus(str, Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"
    DELETED = "deleted"


@dataclass
class Player:
    id: UUID
    display_name: str
    email: str | None = None
    status: PlayerStatus = PlayerStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    platform_links: list[PlatformLink] = field(default_factory=list)

    game_state: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, display_name: str, email: str | None = None) -> "Player":
        """Фабричный метод для создания нового игрока с валидацией"""
        if not display_name or len(display_name.strip()) == 0:
            raise ValueError("Display name cannot be empty")
        return cls(id=uuid4(), display_name=display_name.strip(), email=email)

    def ensure_can_authenticate(self) -> None:
        if self.status != PlayerStatus.ACTIVE:
            raise PlayerInactiveError(f"Player {self.id} is not active")

    def link_platform(
        self,
        platform: PlatformType,
        platform_user_id: str,
        metadata: dict | None = None,
    ) -> PlatformLink:
        self.ensure_can_authenticate()
        if any(link.platform == platform for link in self.platform_links):
            raise PlatformAlreadyLinkedError(platform)

        link = PlatformLink.create(
            player_id=self.id,
            platform=platform,
            platform_user_id=platform_user_id,
            metadata=metadata,
        )
        self.platform_links.append(link)
        self.updated_at = datetime.now(timezone.utc)
        return link

    def unlink_platform(self, platform: PlatformType) -> None:
        link = next((l for l in self.platform_links if l.platform == platform), None)
        if link is None:
            raise ValueError(f"Platform {platform} is not linked")

        # Бизнес-правило: нельзя остаться без способа входа
        other_links = [l for l in self.platform_links if l.platform != platform]
        if not other_links and not self.email:
            raise CannotUnlinkLastAuthMethodError(
                "Cannot unlink the last authentication method without a password"
            )

        self.platform_links.remove(link)
        self.updated_at = datetime.now(timezone.utc)

    def has_platform(self, platform: PlatformType) -> bool:
        return any(link.platform == platform for link in self.platform_links)


    def update_game_state(self, new_state: dict[str, Any]) -> None:
        if not isinstance(new_state, dict):
            raise ValueError("game_state must be a dict")
        self.game_state = dict(new_state)
        self.updated_at = datetime.now(timezone.utc)

    def increment_counter(self, key: str, delta: int = 1) -> None:
        if delta <= 0:
            raise ValueError("delta must be positive")
        current = self.game_state.get(key, 0)
        if not isinstance(current, int):
            raise ValueError(f"counter '{key}' is not an int")
        self.game_state[key] = current + delta
        self.updated_at = datetime.now(timezone.utc)
