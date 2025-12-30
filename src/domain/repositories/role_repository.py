from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import Role


class RoleRepository(ABC):
    @abstractmethod
    def create(self, role: Role) -> Role:
        pass

    @abstractmethod
    def find_by_id(self, role_id: str) -> Optional[Role]:
        pass

    @abstractmethod
    def find_by_company(self, company_id: str) -> List[Role]:
        pass

    @abstractmethod
    def find_by_name(self, company_id: str, name: str) -> Optional[Role]:
        pass

    @abstractmethod
    def find_all(self) -> List[Role]:
        pass

    @abstractmethod
    def update(self, role_id: str, role: Role) -> Optional[Role]:
        pass

    @abstractmethod
    def delete(self, role_id: str) -> bool:
        pass
