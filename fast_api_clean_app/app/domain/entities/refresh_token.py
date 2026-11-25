from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class RefreshToken:
    id: UUID
    player_id: UUID
    token_hash: str
    family_id: UUID
    used: bool
    revoked: bool
    expires_at: datetime
    created_at: datetime
