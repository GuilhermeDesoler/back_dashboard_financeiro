from typing import List, Optional
from datetime import datetime
from src.domain.entities import FinancialEntry
from src.domain.repositories import FinancialEntryRepository


class ListFinancialEntries:
    def __init__(self, repository: FinancialEntryRepository):
        self._repository = repository

    def execute(
        self,
        modality_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[FinancialEntry]:
        if modality_id:
            return self._repository.find_by_modality(modality_id)
        
        if start_date and end_date:
            return self._repository.find_by_date_range(start_date, end_date)
        
        return self._repository.find_all()
