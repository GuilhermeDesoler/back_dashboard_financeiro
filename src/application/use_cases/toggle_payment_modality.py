from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository


class TogglePaymentModality:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(self, modality_id: str, activate: bool) -> PaymentModality:
        modality = self._repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade não encontrada")
        
        if activate:
            modality.activate()
        else:
            modality.deactive()
        
        return self._repository.update(modality)
