from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import Installment


class InstallmentRepository(ABC):
    @abstractmethod
    def create(self, installment: Installment) -> Installment:
        pass

    @abstractmethod
    def find_by_id(self, installment_id: str) -> Optional[Installment]:
        pass

    @abstractmethod
    def find_by_financial_entry_id(self, financial_entry_id: str) -> List[Installment]:
        pass

    @abstractmethod
    def find_all(self) -> List[Installment]:
        pass

    @abstractmethod
    def update(self, installment_id: str, installment: Installment) -> Optional[Installment]:
        pass

    @abstractmethod
    def delete(self, installment_id: str) -> bool:
        pass

    @abstractmethod
    def delete_by_financial_entry_id(self, financial_entry_id: str) -> bool:
        pass
