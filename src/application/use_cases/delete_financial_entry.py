from src.domain.repositories import FinancialEntryRepository


class DeleteFinancialEntry:
    def __init__(self, repository: FinancialEntryRepository):
        self._repository = repository

    def execute(self, entry_id: str) -> bool:
        entry = self._repository.find_by_id(entry_id)
        if not entry:
            raise ValueError("Lançamento não encontrado")
        
        return self._repository.delete(entry_id)
