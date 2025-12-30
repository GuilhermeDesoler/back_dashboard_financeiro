from typing import List
from src.domain.entities import Company
from src.domain.repositories import CompanyRepository


class ListCompanies:
    def __init__(self, company_repository: CompanyRepository):
        self._company_repository = company_repository

    def execute(self, only_active: bool = True) -> List[Company]:
        """
        Lista todas as empresas

        Args:
            only_active: Se True, retorna apenas empresas ativas

        Returns:
            Lista de empresas
        """
        return self._company_repository.find_all(only_active=only_active)
