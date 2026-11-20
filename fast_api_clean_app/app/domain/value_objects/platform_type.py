from enum import Enum
from app.domain.exceptions import InvalidPlatformError

class PlatformType(str, Enum):
    STEAM = "steam"
    EPIC = "epic"
    YANDEX = "yandex"
    XBOX = "xbox"
    PSN = "psn"
    NINTENDO = "nintendo"

    @classmethod
    def from_string(cls, value: str) -> "PlatformType":
        """Безопасный парсинг"""
        try:
            return cls(value.lower())
        except ValueError:
            raise InvalidPlatformError(f"Unsupported platform: {value}")
