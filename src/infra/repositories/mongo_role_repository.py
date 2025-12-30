from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from pymongo.collection import Collection

from src.domain.entities import Role
from src.domain.repositories import RoleRepository


class MongoRoleRepository(RoleRepository):
    def __init__(self, collection: Collection):
        self._collection = collection

    def create(self, role: Role) -> Role:
        role.id = str(uuid4())
        role.created_at = datetime.now()
        role.updated_at = datetime.now()

        role_dict = role.to_dict()
        role_dict["_id"] = role.id
        role_dict.pop("id")

        self._collection.insert_one(role_dict)

        return role

    def find_by_id(self, role_id: str) -> Optional[Role]:
        doc = self._collection.find_one({"_id": role_id})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_by_company(self, company_id: str) -> List[Role]:
        docs = self._collection.find({"company_id": company_id})
        return [self._doc_to_entity(doc) for doc in docs]

    def find_by_name(self, company_id: str, name: str) -> Optional[Role]:
        doc = self._collection.find_one({"company_id": company_id, "name": name})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_all(self) -> List[Role]:
        docs = self._collection.find()
        return [self._doc_to_entity(doc) for doc in docs]

    def update(self, role_id: str, role: Role) -> Optional[Role]:
        role.updated_at = datetime.now()

        role_dict = role.to_dict()
        role_dict.pop("id", None)

        result = self._collection.update_one(
            {"_id": role_id},
            {"$set": role_dict}
        )

        if result.modified_count > 0 or result.matched_count > 0:
            role.id = role_id
            return role

        return None

    def delete(self, role_id: str) -> bool:
        result = self._collection.delete_one({"_id": role_id})
        return result.deleted_count > 0

    def _doc_to_entity(self, doc: dict) -> Role:
        return Role(
            id=doc["_id"],
            name=doc["name"],
            company_id=doc["company_id"],
            feature_ids=doc.get("feature_ids", []),
            description=doc.get("description"),
            created_at=Role._parse_datetime(doc.get("created_at")),
            updated_at=Role._parse_datetime(doc.get("updated_at"))
        )
