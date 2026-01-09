"""
MongoDB implementation of BankLimitRepository
"""
from typing import List, Optional
from datetime import datetime
import uuid
from src.domain.entities.bank_limit import BankLimit
from src.domain.repositories.bank_limit_repository import BankLimitRepository


class MongoBankLimitRepository(BankLimitRepository):
    def __init__(self, collection):
        self.collection = collection

    def create(
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
        limit_id = str(uuid.uuid4())
        now = datetime.utcnow()

        limit_doc = {
            "id": limit_id,
            "bank_name": bank_name,
            "rotativo_available": rotativo_available,
            "rotativo_used": rotativo_used,
            "cheque_available": cheque_available,
            "cheque_used": cheque_used,
            "rotativo_rate": rotativo_rate,
            "cheque_rate": cheque_rate,
            "interest_rate": interest_rate,
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
        }

        self.collection.insert_one(limit_doc)
        return BankLimit.from_dict(limit_doc)

    def find_by_id(self, limit_id: str) -> Optional[BankLimit]:
        doc = self.collection.find_one({"id": limit_id})
        if doc:
            return BankLimit.from_dict(doc)
        return None

    def find_all(self) -> List[BankLimit]:
        docs = self.collection.find().sort("bank_name", 1)
        return [BankLimit.from_dict(doc) for doc in docs]

    def update(
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
        now = datetime.utcnow()

        update_data = {
            "bank_name": bank_name,
            "rotativo_available": rotativo_available,
            "rotativo_used": rotativo_used,
            "cheque_available": cheque_available,
            "cheque_used": cheque_used,
            "rotativo_rate": rotativo_rate,
            "cheque_rate": cheque_rate,
            "interest_rate": interest_rate,
            "updated_at": now.isoformat(),
        }

        result = self.collection.update_one({"id": limit_id}, {"$set": update_data})

        if result.modified_count == 0:
            raise ValueError(f"Bank limit with id {limit_id} not found")

        return self.find_by_id(limit_id)

    def delete(self, limit_id: str) -> bool:
        result = self.collection.delete_one({"id": limit_id})
        return result.deleted_count > 0
