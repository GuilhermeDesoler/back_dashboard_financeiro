from datetime import datetime
from src.domain.entities import FinancialEntry
from src.domain.repositories import FinancialEntryRepository
from src.domain.repositories import PaymentModalityRepository


class UpdateFinancialEntry:
    def __init__(
        self,
        entry_repository: FinancialEntryRepository,
        modality_repository: PaymentModalityRepository
    ):
        self._entry_repository = entry_repository
        self._modality_repository = modality_repository

    def execute(
        self,
        entry_id: str,
        value: float,
        date: datetime,
        modality_id: str
    ) -> FinancialEntry:
        entry = self._entry_repository.find_by_id(entry_id)
        if not entry:
            raise ValueError("Lançamento não encontrado")
        
        if value <= 0:
            raise ValueError("Valor deve ser maior que zero")
        
        modality = self._modality_repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade de pagamento não encontrada")
        
        if not modality.is_active:
            raise ValueError("Modalidade de pagamento está inativa")
        
        entry.value = value
        entry.date = date
        entry.modality_id = modality_id
        entry.modality_name = modality.name
        entry.modality_color = modality.color
        entry.is_credit_plan = modality.is_credit_plan  # Atualiza is_credit_plan

        updated = self._entry_repository.update(entry_id, entry)
        if not updated:
            raise ValueError("Erro ao atualizar lançamento")

        return updated
