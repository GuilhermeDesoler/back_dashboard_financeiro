from datetime import datetime
from src.domain.entities import Installment
from src.domain.repositories import InstallmentRepository


class PayInstallment:
    def __init__(self, repository: InstallmentRepository):
        self._repository = repository

    def execute(self, installment_id: str, payment_date: datetime = None) -> Installment:
        installment = self._repository.find_by_id(installment_id)
        if not installment:
            raise ValueError("Parcela não encontrada")

        if installment.is_paid:
            raise ValueError("Parcela já está paga")

        installment.mark_as_paid(payment_date)

        updated = self._repository.update(installment_id, installment)
        if not updated:
            raise ValueError("Erro ao atualizar parcela")

        return updated
