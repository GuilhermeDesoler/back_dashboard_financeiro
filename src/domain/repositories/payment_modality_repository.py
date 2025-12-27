from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import PaymentModality


class PaymentModalityRepository(ABC):
    @abstractmethod
    def create(self, modality: PaymentModality) -> PaymentModality:
        pass

    @abstractmethod
    def find_by_id(self, modality_id: str) -> Optional[PaymentModality]:
        pass

    @abstractmethod
    def find_all(self) -> List[PaymentModality]:
        pass

    @abstractmethod
    def find_active(self) -> List[PaymentModality]:
        pass

    @abstractmethod
    def update(
        self, modality_id: str, modality: PaymentModality
    ) -> Optional[PaymentModality]:
        pass

    @abstractmethod
    def delete(self, modality_id: str) -> bool:
        pass

    @abstractmethod
    def activate(self, modality_id: str) -> bool:
        pass

    @abstractmethod
    def deactivate(self, modality_id: str) -> bool:
        pass
