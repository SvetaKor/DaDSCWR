from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4
from enum import Enum


class CredentialType(str, Enum):
    PASSWORD = "password"
    OAUTH_YANDEX = "oauth_yandex"


@dataclass
class Credential:
    id: UUID
    player_id: UUID
    type: CredentialType
    secret_hash: str | None
    created_at: datetime
    last_used_at: datetime | None = None

    @classmethod
    def create_with_password(cls, player_id: UUID, password_hash: str) -> "Credential":
        return cls(
            id=uuid4(),
            player_id=player_id,
            type=CredentialType.PASSWORD,
            secret_hash=password_hash,
            created_at=datetime.now(timezone.utc),
        )

    def verify_password(self, plain_password: str, hasher) -> bool:
        if self.type != CredentialType.PASSWORD or not self.secret_hash:
            return False
        return hasher.verify(plain_password, self.secret_hash)

    def mark_used(self) -> None:
        self.last_used_at = datetime.now(timezone.utc)
