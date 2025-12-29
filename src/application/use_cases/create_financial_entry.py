from datetime import datetime
from src.domain.entities import FinancialEntry
from src.domain.repositories import FinancialEntryRepository
from src.domain.repositories import PaymentModalityRepository


class CreateFinancialEntry:
    def __init__(
        self,
        entry_repository: FinancialEntryRepository,
        modality_repository: PaymentModalityRepository
    ):
        self._entry_repository = entry_repository
        self._modality_repository = modality_repository

    def execute(
        self, value: float, date: datetime, modality_id: str
    ) -> FinancialEntry:
        if value <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        modality = self._modality_repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade de pagamento não encontrada")
        
        if not modality.is_active:
            raise ValueError("Modalidade de pagamento está inativa")
        
        entry = FinancialEntry(
            value=value,
            date=date,
            modality_id=modality_id,
            modality_name=modality.name,
            modality_color=modality.color
        )
        
        return self._entry_repository.create(entry)
