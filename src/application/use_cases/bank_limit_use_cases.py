"""
Bank Limit Use Cases
"""
from typing import List
from src.domain.entities.bank_limit import BankLimit
from src.domain.repositories.bank_limit_repository import BankLimitRepository


class CreateBankLimit:
    def __init__(self, repository: BankLimitRepository):
        self.repository = repository

    def execute(
        self,
        bank_name: str,
        rotativo_available: float = 0.0,
        rotativo_used: float = 0.0,
        cheque_available: float = 0.0,
        cheque_used: float = 0.0,
        rotativo_rate: float = 0.0,
        cheque_rate: float = 0.0,
        interest_rate: float = 0.0,
    ) -> BankLimit:
        if not bank_name or not bank_name.strip():
            raise ValueError("Bank name is required")

        return self.repository.create(
            bank_name=bank_name.strip(),
            rotativo_available=rotativo_available,
            rotativo_used=rotativo_used,
            cheque_available=cheque_available,
            cheque_used=cheque_used,
            rotativo_rate=rotativo_rate,
            cheque_rate=cheque_rate,
            interest_rate=interest_rate,
        )


class ListBankLimits:
    def __init__(self, repository: BankLimitRepository):
        self.repository = repository

    def execute(self) -> List[BankLimit]:
        return self.repository.find_all()


class UpdateBankLimit:
    def __init__(self, repository: BankLimitRepository):
        self.repository = repository

    def execute(
        self,
        limit_id: str,
        bank_name: str,
        rotativo_available: float = 0.0,
        rotativo_used: float = 0.0,
        cheque_available: float = 0.0,
        cheque_used: float = 0.0,
        rotativo_rate: float = 0.0,
        cheque_rate: float = 0.0,
        interest_rate: float = 0.0,
    ) -> BankLimit:
        if not bank_name or not bank_name.strip():
            raise ValueError("Bank name is required")

        return self.repository.update(
            limit_id=limit_id,
            bank_name=bank_name.strip(),
            rotativo_available=rotativo_available,
            rotativo_used=rotativo_used,
            cheque_available=cheque_available,
            cheque_used=cheque_used,
            rotativo_rate=rotativo_rate,
            cheque_rate=cheque_rate,
            interest_rate=interest_rate,
        )


class DeleteBankLimit:
    def __init__(self, repository: BankLimitRepository):
        self.repository = repository

    def execute(self, limit_id: str) -> bool:
        success = self.repository.delete(limit_id)
        if not success:
            raise ValueError(f"Bank limit with id {limit_id} not found")
        return success
