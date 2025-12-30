from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository


class CreatePaymentModality:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(self, name: str, color: str, is_active: bool = True) -> PaymentModality:
        if not name or not name.strip():
            raise ValueError("Nome da modalidade é obrigatório")

        if not color or not color.strip():
            raise ValueError("Cor da modalidade é obrigatória")

        existing = self._repository.find_by_name(name)
        if existing:
            raise ValueError(f"Modalidade '{name}' já existe")

        modality = PaymentModality(name=name.strip(), color=color.strip(), is_active=is_active)

        return self._repository.create(modality)
