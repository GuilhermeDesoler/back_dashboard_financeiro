from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.domain.entities import FinancialEntry


class FinancialEntryRepository(ABC):
    @abstractmethod
    def create(self, entry: FinancialEntry) -> FinancialEntry:
        pass

    @abstractmethod
    def find_by_id(self, entry_id: str) -> Optional[FinancialEntry]:
        pass

    @abstractmethod
    def find_all(self) -> List[FinancialEntry]:
        pass

    @abstractmethod
    def find_by_date(self, date: datetime) -> List[FinancialEntry]:
        pass

    @abstractmethod
    def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[FinancialEntry]:
        pass

    @abstractmethod
    def find_by_modality(self, modality_id: str) -> List[FinancialEntry]:
        pass

    @abstractmethod
    def update(self, entry_id: str, entry: FinancialEntry) -> Optional[FinancialEntry]:
        pass

    @abstractmethod
    def delete(self, entry_id: str) -> bool:
        pass

    @abstractmethod
    def get_total_by_date(self, date: datetime) -> float:
        pass

    @abstractmethod
    def get_total_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> float:
        pass
