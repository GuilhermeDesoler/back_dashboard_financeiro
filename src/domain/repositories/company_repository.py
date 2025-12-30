from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import Company


class CompanyRepository(ABC):
    @abstractmethod
    def create(self, company: Company) -> Company:
        pass

    @abstractmethod
    def find_by_id(self, company_id: str) -> Optional[Company]:
        pass

    @abstractmethod
    def find_by_cnpj(self, cnpj: str) -> Optional[Company]:
        pass

    @abstractmethod
    def find_all(self, only_active: bool = True) -> List[Company]:
        pass

    @abstractmethod
    def update(self, company_id: str, company: Company) -> Optional[Company]:
        pass

    @abstractmethod
    def delete(self, company_id: str) -> bool:
        pass
