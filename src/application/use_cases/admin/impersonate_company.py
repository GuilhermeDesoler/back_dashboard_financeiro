from typing import Dict
from src.domain.repositories import CompanyRepository, UserRepository, RoleRepository, FeatureRepository
from src.infra.security import JWTHandler


class ImpersonateCompany:
    def __init__(
        self,
        company_repository: CompanyRepository,
        user_repository: UserRepository,
        role_repository: RoleRepository,
        feature_repository: FeatureRepository,
        jwt_handler: JWTHandler
    ):
        self._company_repository = company_repository
        self._user_repository = user_repository
        self._role_repository = role_repository
        self._feature_repository = feature_repository
        self._jwt_handler = jwt_handler

    def execute(self, super_admin_user_id: str, target_company_id: str) -> Dict:
        """
        Gera um token JWT para o super admin acessar uma empresa específica
        (impersonate)

        Args:
            super_admin_user_id: ID do super admin fazendo impersonate
            target_company_id: ID da empresa alvo

        Returns:
            Dict com token de impersonate e dados da empresa

        Raises:
            ValueError: Se empresa não existir ou usuário não for super admin
        """
        # Verifica se o usuário é super admin
        user = self._user_repository.find_by_id(super_admin_user_id)
        if not user or not user.is_super_admin:
            raise ValueError("Apenas super administradores podem fazer impersonate")

        # Verifica se a empresa existe
        company = self._company_repository.find_by_id(target_company_id)
        if not company:
            raise ValueError("Empresa não encontrada")

        if not company.is_active:
            raise ValueError("Empresa inativa")

        # Busca todas as features do sistema para o super admin
        all_features = self._feature_repository.find_all()
        feature_codes = [f.code for f in all_features if f.is_system]

        # Gera payload do JWT com contexto da empresa alvo
        payload = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "company_id": target_company_id,  # Empresa alvo para impersonate
            "roles": ["Super Admin"],
            "features": feature_codes,  # Todas as features
            "is_super_admin": True,
            "impersonating": True,  # Flag para indicar impersonate
            "original_company_id": user.company_id  # Empresa original do super admin
        }

        # Gera token com validade de 1 hora
        token = self._jwt_handler.generate_token(payload, expires_in_hours=1)

        return {
            "token": token,
            "company": company.to_dict(),
            "message": f"Impersonando empresa: {company.name}",
            "expires_in_hours": 1
        }
