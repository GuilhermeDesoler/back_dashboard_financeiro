from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import User


class UserRepository(ABC):
    @abstractmethod
    def create(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_id(self, user_id: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[User]:
        pass

    @abstractmethod
    def find_by_company(self, company_id: str) -> List[User]:
        pass

    @abstractmethod
    def find_all(self) -> List[User]:
        pass

    @abstractmethod
    def update(self, user_id: str, user: User) -> Optional[User]:
        pass

    @abstractmethod
    def delete(self, user_id: str) -> bool:
        pass

    @abstractmethod
    def activate(self, user_id: str) -> bool:
        pass

    @abstractmethod
    def deactivate(self, user_id: str) -> bool:
        pass
