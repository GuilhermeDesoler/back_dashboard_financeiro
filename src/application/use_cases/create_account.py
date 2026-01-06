from datetime import datetime
from src.domain.entities import Account
from src.domain.repositories import AccountRepository


class CreateAccount:
    def __init__(self, account_repository: AccountRepository):
        self._account_repository = account_repository

    def execute(
        self,
        value: float,
        date: datetime,
        description: str,
        account_type: str
    ) -> Account:
        if value <= 0:
            raise ValueError("Valor deve ser maior que zero")

        if not description or not description.strip():
            raise ValueError("Descrição é obrigatória")

        if account_type not in ["boleto", "payment", "investment"]:
            raise ValueError("Tipo de conta inválido. Use: boleto, payment ou investment")

        account = Account(
            value=value,
            date=date,
            description=description.strip(),
            type=account_type
        )

        return self._account_repository.create(account)
