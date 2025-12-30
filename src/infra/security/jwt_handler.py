import jwt
import os
from datetime import datetime, timedelta
from typing import Dict, Optional


class JWTHandler:
    def __init__(self, secret_key: Optional[str] = None):
        self.secret_key = secret_key or os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
        self.algorithm = "HS256"

    def generate_token(self, payload: Dict, expires_in_hours: int = 24) -> str:
        """
        Gera um token JWT

        Args:
            payload: Dados a serem incluídos no token
            expires_in_hours: Tempo de expiração em horas

        Returns:
            Token JWT codificado
        """
        payload_copy = payload.copy()
        payload_copy["exp"] = datetime.utcnow() + timedelta(hours=expires_in_hours)
        payload_copy["iat"] = datetime.utcnow()

        return jwt.encode(payload_copy, self.secret_key, algorithm=self.algorithm)

    def verify_token(self, token: str) -> Dict:
        """
        Verifica e decodifica um token JWT

        Args:
            token: Token JWT a ser verificado

        Returns:
            Payload decodificado

        Raises:
            ValueError: Se o token for inválido ou expirado
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("Token expirado")
        except jwt.InvalidTokenError:
            raise ValueError("Token inválido")

    def generate_refresh_token(self, payload: Dict) -> str:
        """
        Gera um refresh token com tempo de expiração maior

        Args:
            payload: Dados a serem incluídos no token

        Returns:
            Refresh token JWT
        """
        return self.generate_token(payload, expires_in_hours=24 * 7)  # 7 dias
