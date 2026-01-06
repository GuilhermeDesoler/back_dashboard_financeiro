from typing import List
from src.domain.entities import Installment
from src.domain.repositories import InstallmentRepository


class ListInstallments:
    def __init__(self, repository: InstallmentRepository):
        self._repository = repository

    def execute(self, financial_entry_id: str = None) -> List[Installment]:
        if financial_entry_id:
            return self._repository.find_by_financial_entry_id(financial_entry_id)
        return self._repository.find_all()
