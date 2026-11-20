import re
from dataclasses import dataclass

from app.domain.exceptions import InvalidEmailError

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(pattern, self.value):
            raise InvalidEmailError(f"Invalid email: {self.value}")
