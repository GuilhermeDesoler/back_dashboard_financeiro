from src.domain.repositories import PaymentModalityRepository


class DeletePaymentModality:
    def __init__(self, repository: PaymentModalityRepository):
        self._repository = repository

    def execute(self, modality_id: str) -> bool:
        modality = self._repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade não encontrada")
        
        return self._repository.delete(modality_id)
