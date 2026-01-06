from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.domain.entities import Account


class AccountRepository(ABC):
    @abstractmethod
    def create(self, account: Account) -> Account:
        pass

    @abstractmethod
    def find_by_id(self, account_id: str) -> Optional[Account]:
        pass

    @abstractmethod
    def find_all(self) -> List[Account]:
        pass

    @abstractmethod
    def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Account]:
        pass

    @abstractmethod
    def delete(self, account_id: str) -> bool:
        pass
