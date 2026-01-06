from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from pymongo.collection import Collection

from src.domain.entities import Installment
from src.domain.repositories import InstallmentRepository


class MongoInstallmentRepository(InstallmentRepository):
    def __init__(self, collection: Collection):
        self._collection = collection

    def create(self, installment: Installment) -> Installment:
        installment.id = str(uuid4())
        installment.created_at = datetime.now()
        installment.updated_at = datetime.now()

        installment_dict = installment.to_dict()
        installment_dict['_id'] = installment.id
        installment_dict.pop('id')

        self._collection.insert_one(installment_dict)

        return installment

    def find_by_id(self, installment_id: str) -> Optional[Installment]:
        doc = self._collection.find_one({"_id": installment_id})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_by_financial_entry_id(self, financial_entry_id: str) -> List[Installment]:
        docs = self._collection.find({"financial_entry_id": financial_entry_id}).sort("installment_number", 1)
        return [self._doc_to_entity(doc) for doc in docs]

    def find_all(self) -> List[Installment]:
        docs = self._collection.find().sort("due_date", 1)
        return [self._doc_to_entity(doc) for doc in docs]

    def update(self, installment_id: str, installment: Installment) -> Optional[Installment]:
        installment.updated_at = datetime.now()

        installment_dict = installment.to_dict()
        installment_dict.pop('id', None)

        result = self._collection.update_one(
            {"_id": installment_id},
            {"$set": installment_dict}
        )

        if result.modified_count > 0 or result.matched_count > 0:
            installment.id = installment_id
            return installment

        return None

    def delete(self, installment_id: str) -> bool:
        result = self._collection.delete_one({"_id": installment_id})
        return result.deleted_count > 0

    def delete_by_financial_entry_id(self, financial_entry_id: str) -> bool:
        result = self._collection.delete_many({"financial_entry_id": financial_entry_id})
        return result.deleted_count > 0

    def _doc_to_entity(self, doc: dict) -> Installment:
        return Installment(
            id=doc["_id"],
            financial_entry_id=doc["financial_entry_id"],
            installment_number=doc["installment_number"],
            total_installments=doc["total_installments"],
            amount=doc["amount"],
            due_date=Installment._parse_datetime(doc["due_date"]),
            is_paid=doc.get("is_paid", False),
            payment_date=Installment._parse_datetime(doc.get("payment_date")),
            created_at=Installment._parse_datetime(doc.get("created_at")),
            updated_at=Installment._parse_datetime(doc.get("updated_at"))
        )
