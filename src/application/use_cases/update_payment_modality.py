from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository


class UpdatePaymentModality:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(self, modality_id: str, name: str) -> PaymentModality:
        modality = self._repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade não encontrada")
        
        if not name or not name.strip():
            raise ValueError("Nome da modalidade é obrigatório")
        
        existing = self._repository.find_by_name(name)
        if existing and existing.id != modality_id:
            raise ValueError(f"Modalidade '{name}' já existe")
        
        modality.name = name.strip()
        
        return self._repository.update(modality)
