from src.domain.repositories.account_repository import AccountRepository
from src.domain.entities.account import Account
from datetime import datetime


class UpdateAccount:
    def __init__(self, repository: AccountRepository):
        self.repository = repository

    def execute(self, account_id: str, paid: bool = None, value: float = None,
                date: datetime = None, description: str = None) -> Account:
        account = self.repository.find_by_id(account_id)

        if account is None:
            raise ValueError(f"Account with id {account_id} not found")

        if paid is not None:
            account.paid = paid
        if value is not None:
            account.value = value
        if date is not None:
            account.date = date
        if description is not None:
            account.description = description

        return self.repository.update(account)
