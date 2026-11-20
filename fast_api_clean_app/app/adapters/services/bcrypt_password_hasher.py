import bcrypt

from app.domain.services.password_hasher import PasswordHasher


class BcryptPasswordHasher(PasswordHasher):
    def __init__(self, rounds: int = 12) -> None:
        self._rounds = rounds

    def hash(self, plain: str) -> str:
        return bcrypt.hashpw(
            plain.encode("utf-8"),
            bcrypt.gensalt(rounds=self._rounds),
        ).decode("utf-8")

    def verify(self, plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except (ValueError, TypeError):
            # При невалидном хеше считаем пароль неверным. Так timing-защита работает предсказуемо
            return False
