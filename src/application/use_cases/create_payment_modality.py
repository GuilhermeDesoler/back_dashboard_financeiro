from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository


class CreatePaymentModality:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(self, name: str) -> PaymentModality:
        if not name or not name.strip():
            raise ValueError("Nome da modalidade é obrigatório")
        
        existing = self._repository.find_by_name(name)
        if existing:
            raise ValueError(f"Modalidade '{name}' já existe")
        
        modality = PaymentModality(name=name.strip(), is_active=True)
        
        return self._repository.create(modality)
