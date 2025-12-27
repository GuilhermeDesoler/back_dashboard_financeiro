from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from pymongo.collection import Collection

from src.domain.entities import PaymentModality
from src.domain.repositories import PaymentModalityRepository

class MongoPaymentModalityRepository(PaymentModalityRepository):
    def __init__(self, collection: Collection):
        self._collection = collection

    def create(self, modality: PaymentModality) -> PaymentModality:
        modality.id = str(uuid4())
        modality.created_at = datetime.now()
        modality.updated_at = datetime.now()
        
        modality_dict = modality.to_dict()
        modality_dict['_id'] = modality.id
        modality_dict.pop('id')
        
        self._collection.insert_one(modality_dict)
        
        return modality

    def find_by_id(self, modality_id: str) -> Optional[PaymentModality]:
        doc = self._collection.find_one({"_id": modality_id})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_all(self) -> List[PaymentModality]:
        docs = self._collection.find()
        return [self._doc_to_entity(doc) for doc in docs]

    def update(self, modality: PaymentModality) -> PaymentModality:
        modality.updated_at = datetime.now()
        
        modality_dict = modality.to_dict()
        modality_id = modality_dict.pop('id')
        
        self._collection.update_one(
            {"_id": modality_id},
            {"$set": modality_dict}
        )
        
        return modality

    def delete(self, modality_id: str) -> bool:
        result = self._collection.delete_one({"_id": modality_id})
        return result.deleted_count > 0

    def find_by_name(self, name: str) -> Optional[PaymentModality]:
        doc = self._collection.find_one({"name": name})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def _doc_to_entity(self, doc: dict) -> PaymentModality:
        return PaymentModality(
            id=doc["_id"],
            name=doc["name"],
            is_active=doc.get("is_active", True),
            created_at=PaymentModality._parse_datetime(doc.get("created_at")),
            updated_at=PaymentModality._parse_datetime(doc.get("updated_at"))
        )