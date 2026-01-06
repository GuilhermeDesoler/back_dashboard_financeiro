from typing import List, Optional
from datetime import datetime
from src.domain.entities import Account
from src.domain.repositories import AccountRepository


class ListAccounts:
    def __init__(self, account_repository: AccountRepository):
        self._account_repository = account_repository

    def execute(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Account]:
        if start_date and end_date:
            return self._account_repository.find_by_date_range(start_date, end_date)
        return self._account_repository.find_all()
