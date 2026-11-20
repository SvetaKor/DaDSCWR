from app.domain.exceptions import WeakPasswordError


class PasswordPolicy:
    """
    Доменный сервис проверки сложности пароля
    """

    MIN_LENGTH = 8
    MAX_LENGTH = 128

    def validate(self, plain: str) -> None:
        if len(plain) < self.MIN_LENGTH:
            raise WeakPasswordError(
                f"Password must be at least {self.MIN_LENGTH} characters"
            )
        if len(plain) > self.MAX_LENGTH:
            raise WeakPasswordError(
                f"Password must be at most {self.MAX_LENGTH} characters"
            )
        if plain.isdigit() or plain.isalpha():
            raise WeakPasswordError(
                "Password must contain both letters and digits"
            )
