from typing import List
from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository


class ListPaymentModalities:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(self, only_active: bool = True) -> List[PaymentModality]:
        modalities = self._repository.find_all()
        
        if only_active:
            return [m for m in modalities if m.is_active]
        
        return modalities
