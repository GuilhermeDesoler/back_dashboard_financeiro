from src.domain.entities import Company
from src.domain.repositories import CompanyRepository
from src.database import create_tenant_db


class CreateCompany:
    def __init__(self, company_repository: CompanyRepository):
        self._company_repository = company_repository

    def execute(self, name: str, cnpj: str, phone: str, plan: str = "basic") -> Company:
        """
        Cria uma nova empresa

        Args:
            name: Nome da empresa
            cnpj: CNPJ da empresa
            phone: Telefone da empresa
            plan: Plano da empresa (basic, premium, enterprise)

        Returns:
            Company criada

        Raises:
            ValueError: Se dados forem inválidos ou CNPJ já existir
        """
        # Validações
        if not name or not name.strip():
            raise ValueError("Nome da empresa é obrigatório")

        if not cnpj or not cnpj.strip():
            raise ValueError("CNPJ é obrigatório")

        if not phone or not phone.strip():
            raise ValueError("Telefone é obrigatório")

        # Verifica se CNPJ já existe
        existing_company = self._company_repository.find_by_cnpj(cnpj)
        if existing_company:
            raise ValueError("CNPJ já cadastrado")

        # Cria a empresa
        company = Company(
            name=name.strip(),
            cnpj=cnpj.strip(),
            phone=phone.strip(),
            plan=plan
        )

        created_company = self._company_repository.create(company)

        # Cria o banco de dados da empresa com índices
        create_tenant_db(created_company.id)

        return created_company
