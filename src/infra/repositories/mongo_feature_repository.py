from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from pymongo.collection import Collection

from src.domain.entities import Feature
from src.domain.repositories import FeatureRepository


class MongoFeatureRepository(FeatureRepository):
    def __init__(self, collection: Collection):
        self._collection = collection

    def create(self, feature: Feature) -> Feature:
        feature.id = str(uuid4())
        feature.created_at = datetime.now()

        feature_dict = feature.to_dict()
        feature_dict["_id"] = feature.id
        feature_dict.pop("id")

        self._collection.insert_one(feature_dict)

        return feature

    def find_by_id(self, feature_id: str) -> Optional[Feature]:
        doc = self._collection.find_one({"_id": feature_id})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_by_code(self, code: str) -> Optional[Feature]:
        doc = self._collection.find_one({"code": code})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_by_module(self, module: str) -> List[Feature]:
        docs = self._collection.find({"module": module})
        return [self._doc_to_entity(doc) for doc in docs]

    def find_all(self) -> List[Feature]:
        docs = self._collection.find()
        return [self._doc_to_entity(doc) for doc in docs]

    def find_system_features(self) -> List[Feature]:
        docs = self._collection.find({"is_system": True})
        return [self._doc_to_entity(doc) for doc in docs]

    def delete(self, feature_id: str) -> bool:
        result = self._collection.delete_one({"_id": feature_id})
        return result.deleted_count > 0

    def _doc_to_entity(self, doc: dict) -> Feature:
        return Feature(
            id=doc["_id"],
            code=doc["code"],
            name=doc["name"],
            description=doc["description"],
            module=doc["module"],
            is_system=doc.get("is_system", True),
            created_at=Feature._parse_datetime(doc.get("created_at"))
        )
