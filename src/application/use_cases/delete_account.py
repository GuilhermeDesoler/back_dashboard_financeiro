from src.domain.repositories import AccountRepository


class DeleteAccount:
    def __init__(self, account_repository: AccountRepository):
        self._account_repository = account_repository

    def execute(self, account_id: str) -> bool:
        account = self._account_repository.find_by_id(account_id)
        if not account:
            raise ValueError("Conta não encontrada")

        return self._account_repository.delete(account_id)
