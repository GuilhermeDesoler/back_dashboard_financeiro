import bcrypt


class PasswordHash:
    @staticmethod
    def hash(password: str) -> str:
        """
        Gera um hash seguro da senha usando bcrypt
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def verify(password: str, hashed_password: str) -> bool:
        """
        Verifica se a senha corresponde ao hash
        """
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
