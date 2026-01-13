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
        # Ordena por created_at descendente (mais recente primeiro)
        docs = self._collection.find().sort("created_at", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def find_by_date(self, date: datetime) -> List[FinancialEntry]:
        """Busca lançamentos de uma data específica"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        docs = self._collection.find({
            "date": {
                "$gte": start_of_day.isoformat(),
                "$lte": end_of_day.isoformat()
            }
        }).sort("created_at", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def update(self, entry_id: str, entry: FinancialEntry) -> Optional[FinancialEntry]:
        entry.updated_at = datetime.now()

        entry_dict = entry.to_dict()
        entry_dict.pop('id', None)

        result = self._collection.update_one(
            {"_id": entry_id},
            {"$set": entry_dict}
        )

        if result.modified_count > 0 or result.matched_count > 0:
            entry.id = entry_id
            return entry

        return None

    def delete(self, entry_id: str) -> bool:
        result = self._collection.delete_one({"_id": entry_id})
        return result.deleted_count > 0

    def find_by_modality(self, modality_id: str) -> List[FinancialEntry]:
        docs = self._collection.find({"modality_id": modality_id}).sort("created_at", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[FinancialEntry]:
        docs = self._collection.find({
            "date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }).sort("created_at", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def get_total_by_date(self, date: datetime) -> float:
        """Retorna o total de lançamentos de uma data específica"""
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_of_day.isoformat(),
                        "$lte": end_of_day.isoformat()
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$value"}
                }
            }
        ]

        result = list(self._collection.aggregate(pipeline))
        return float(result[0]["total"]) if result else 0.0

    def get_total_by_date_range(self, start_date: datetime, end_date: datetime) -> float:
        """Retorna o total de lançamentos em um intervalo de datas"""
        pipeline = [
            {
                "$match": {
                    "date": {
                        "$gte": start_date.isoformat(),
                        "$lte": end_date.isoformat()
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total": {"$sum": "$value"}
                }
            }
        ]

        result = list(self._collection.aggregate(pipeline))
        return float(result[0]["total"]) if result else 0.0

    def _doc_to_entity(self, doc: dict) -> FinancialEntry:
        return FinancialEntry(
            id=doc["_id"],
            value=float(doc["value"]),
            date=FinancialEntry._parse_datetime_required(doc["date"]),
            modality_id=doc["modality_id"],
            modality_name=doc["modality_name"],
            modality_color=doc.get("modality_color", "#000000"),
            type=doc.get("type", "received"),
            entry_type=doc.get("entry_type", "normal"),
            is_credit_plan=doc.get("is_credit_plan", False),
            credit_payment=doc.get("credit_payment", False),
            created_at=FinancialEntry._parse_datetime(doc.get("created_at")),
            updated_at=FinancialEntry._parse_datetime(doc.get("updated_at"))
        )
