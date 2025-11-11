import bcrypt

from src.domain.ports import PasswordManager


class BcryptPasswordManager(PasswordManager):
    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def verify(self, password: str, password_hash: str) -> bool:
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'), password_hash.encode('utf-8')
            )
        except (ValueError, TypeError):
            return False
