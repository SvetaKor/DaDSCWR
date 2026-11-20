from typing import Protocol


class PasswordHasher(Protocol):
    """
    Доменный интерфейс хеширования паролей
    """

    def hash(self, plain: str) -> str:
        ...

    def verify(self, plain: str, hashed: str) -> bool:
        """
        Проверка пароля
        """
        ...
