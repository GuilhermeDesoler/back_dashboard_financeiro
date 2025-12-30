from typing import Dict
from src.domain.repositories import UserRepository, RoleRepository, FeatureRepository
from src.infra.security import PasswordHash, JWTHandler


class Login:
    def __init__(
        self,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        feature_repository: FeatureRepository,
        jwt_handler: JWTHandler
    ):
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._feature_repository = feature_repository
        self._jwt_handler = jwt_handler

    def execute(self, email: str, password: str) -> Dict:
        """
        Autentica um usuário e retorna token JWT

        Args:
            email: Email do usuário
            password: Senha do usuário

        Returns:
            Dict com token, refresh_token e dados do usuário

        Raises:
            ValueError: Se credenciais forem inválidas
        """
        if not email or not password:
            raise ValueError("Email e senha são obrigatórios")

        user = self._user_repository.find_by_email(email)
        if not user:
            raise ValueError("Credenciais inválidas")

        if not user.is_active:
            raise ValueError("Usuário inativo")

        if not PasswordHash.verify(password, user.password_hash):
            raise ValueError("Credenciais inválidas")

        # Busca features do usuário baseado em suas roles
        feature_codes = set()
        roles = []

        for role_id in user.role_ids:
            role = self._role_repository.find_by_id(role_id)
            if role:
                roles.append(role.name)
                feature_codes.update(role.feature_ids)

        # Busca os códigos das features
        features = []
        for feature_id in feature_codes:
            feature = self._feature_repository.find_by_id(feature_id)
            if feature:
                features.append(feature.code)

        # Gera payload do JWT
        payload = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "company_id": user.company_id,
            "roles": roles,
            "features": features,
            "is_super_admin": user.is_super_admin
        }

        # Gera tokens
        token = self._jwt_handler.generate_token(payload)
        refresh_token = self._jwt_handler.generate_refresh_token({
            "user_id": user.id,
            "email": user.email,
            "company_id": user.company_id,
            "is_super_admin": user.is_super_admin
        })

        return {
            "token": token,
            "refresh_token": refresh_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "company_id": user.company_id,
                "roles": roles,
                "features": features,
                "is_super_admin": user.is_super_admin
            }
        }
