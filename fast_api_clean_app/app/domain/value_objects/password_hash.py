from dataclasses import dataclass

from app.domain.exceptions import InvalidPasswordHashError


@dataclass(frozen=True)
class PasswordHash:
    """
    Неизменяемый value object, гарантирующий, что внутри - валидный хеш, а не plaintext-пароль.
    
    Проверка основана на префиксах известных алгоритмов хеширования:
      - bcrypt:      $2a$, $2b$, $2y$
      - argon2:      $argon2id$, $argon2i$, $argon2d$
      - scrypt:      $scrypt$
      - pbkdf2:      $pbkdf2$
    """
    value: str

    _KNOWN_PREFIXES: tuple[str, ...] = (
        "$2a$", "$2b$", "$2y$",
        "$argon2id$", "$argon2i$", "$argon2d$",
        "$scrypt$", "$pbkdf2",
    )
    _MIN_LENGTH: int = 20

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not self.value:
            raise InvalidPasswordHashError("Password hash cannot be empty")
        if len(self.value) < self._MIN_LENGTH:
            raise InvalidPasswordHashError(
                "Password hash is too short to be a real hash "
                "(looks like plaintext)"
            )
        if not any(self.value.startswith(p) for p in self._KNOWN_PREFIXES):
            raise InvalidPasswordHashError(
                "Password hash does not match any known algorithm format. "
                "Did you forget to hash the password?"
            )

    def __str__(self) -> str:
        return self.value
