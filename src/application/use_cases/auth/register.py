from src.domain.entities import User
from src.domain.repositories import UserRepository, CompanyRepository
from src.infra.security import PasswordHash


class Register:
    def __init__(
        self,
        user_repository: UserRepository,
        company_repository: CompanyRepository
    ):
        self._user_repository = user_repository
        self._company_repository = company_repository

    def execute(
        self,
        email: str,
        password: str,
        name: str,
        company_id: str
    ) -> User:
        """
        Registra um novo usuário em uma empresa existente

        Args:
            email: Email do usuário
            password: Senha do usuário
            name: Nome do usuário
            company_id: ID da empresa

        Returns:
            User criado

        Raises:
            ValueError: Se dados forem inválidos ou já existirem
        """
        # Validações
        if not email or not email.strip():
            raise ValueError("Email é obrigatório")

        if not password or len(password) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")

        if not name or not name.strip():
            raise ValueError("Nome é obrigatório")

        if not company_id or not company_id.strip():
            raise ValueError("company_id é obrigatório")

        # Verifica se email já existe
        existing_user = self._user_repository.find_by_email(email)
        if existing_user:
            raise ValueError("Email já cadastrado")

        # Verifica se empresa existe
        company = self._company_repository.find_by_id(company_id)
        if not company:
            raise ValueError("Empresa não encontrada")

        if not company.is_active:
            raise ValueError("Empresa inativa")

        # Cria o usuário
        password_hash = PasswordHash.hash(password)
        user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            name=name.strip(),
            company_id=company_id,
            role_ids=[],  # Sem roles inicialmente - admin da empresa deve atribuir
            is_active=True,
            is_super_admin=False
        )

        return self._user_repository.create(user)
