from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from pymongo.collection import Collection

from src.domain.entities import FinancialEntry
from src.domain.repositories import FinancialEntryRepository


class MongoFinancialEntryRepository(FinancialEntryRepository):
    def __init__(self, collection: Collection):
        self._collection = collection

    def create(self, entry: FinancialEntry) -> FinancialEntry:
        entry.id = str(uuid4())
        entry.created_at = datetime.now()
        entry.updated_at = datetime.now()
        
        entry_dict = entry.to_dict()
        entry_dict['_id'] = entry.id
        entry_dict.pop('id')
        
        self._collection.insert_one(entry_dict)
        
        return entry

    def find_by_id(self, entry_id: str) -> Optional[FinancialEntry]:
        doc = self._collection.find_one({"_id": entry_id})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_all(self) -> List[FinancialEntry]:
        docs = self._collection.find().sort("date", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def update(self, entry: FinancialEntry) -> FinancialEntry:
        entry.updated_at = datetime.now()
        
        entry_dict = entry.to_dict()
        entry_id = entry_dict.pop('id')
        
        self._collection.update_one(
            {"_id": entry_id},
            {"$set": entry_dict}
        )
        
        return entry

    def delete(self, entry_id: str) -> bool:
        result = self._collection.delete_one({"_id": entry_id})
        return result.deleted_count > 0

    def find_by_modality(self, modality_id: str) -> List[FinancialEntry]:
        docs = self._collection.find({"modality_id": modality_id}).sort("date", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[FinancialEntry]:
        docs = self._collection.find({
            "date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }).sort("date", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def _doc_to_entity(self, doc: dict) -> FinancialEntry:
        return FinancialEntry(
            id=doc["_id"],
            value=float(doc["value"]),
            date=FinancialEntry._parse_datetime_required(doc["date"]),
            modality_id=doc["modality_id"],
            modality_name=doc["modality_name"],
            created_at=FinancialEntry._parse_datetime(doc.get("created_at")),
            updated_at=FinancialEntry._parse_datetime(doc.get("updated_at"))
        )
