from typing import Dict
from src.domain.repositories import UserRepository, RoleRepository, FeatureRepository
from src.infra.security import JWTHandler


class RefreshToken:
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

    def execute(self, refresh_token: str) -> Dict:
        """
        Gera um novo token a partir do refresh token

        Args:
            refresh_token: Refresh token JWT

        Returns:
            Dict com novo token e refresh_token

        Raises:
            ValueError: Se refresh token for inválido
        """
        try:
            payload = self._jwt_handler.verify_token(refresh_token)
        except ValueError as e:
            raise ValueError(f"Refresh token inválido: {str(e)}")

        user_id = payload.get("user_id")
        if not user_id:
            raise ValueError("Refresh token inválido")

        user = self._user_repository.find_by_id(user_id)
        if not user:
            raise ValueError("Usuário não encontrado")

        if not user.is_active:
            raise ValueError("Usuário inativo")

        # Busca features do usuário
        feature_codes = set()
        roles = []

        for role_id in user.role_ids:
            role = self._role_repository.find_by_id(role_id)
            if role:
                roles.append(role.name)
                feature_codes.update(role.feature_ids)

        features = []
        for feature_id in feature_codes:
            feature = self._feature_repository.find_by_id(feature_id)
            if feature:
                features.append(feature.code)

        # Gera novo payload
        new_payload = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "company_id": user.company_id,
            "roles": roles,
            "features": features
        }

        # Gera novos tokens
        token = self._jwt_handler.generate_token(new_payload)
        new_refresh_token = self._jwt_handler.generate_refresh_token({
            "user_id": user.id,
            "email": user.email,
            "company_id": user.company_id
        })

        return {
            "token": token,
            "refresh_token": new_refresh_token
        }
