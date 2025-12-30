from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from pymongo.collection import Collection

from src.domain.entities import User
from src.domain.repositories import UserRepository


class MongoUserRepository(UserRepository):
    def __init__(self, collection: Collection):
        self._collection = collection

    def create(self, user: User) -> User:
        user.id = str(uuid4())
        user.created_at = datetime.now()
        user.updated_at = datetime.now()

        user_dict = user.to_dict()
        user_dict["_id"] = user.id
        user_dict["password_hash"] = user.password_hash
        user_dict.pop("id")

        self._collection.insert_one(user_dict)

        return user

    def find_by_id(self, user_id: str) -> Optional[User]:
        doc = self._collection.find_one({"_id": user_id})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_by_email(self, email: str) -> Optional[User]:
        doc = self._collection.find_one({"email": email})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_by_company(self, company_id: str) -> List[User]:
        docs = self._collection.find({"company_id": company_id})
        return [self._doc_to_entity(doc) for doc in docs]

    def find_all(self) -> List[User]:
        docs = self._collection.find()
        return [self._doc_to_entity(doc) for doc in docs]

    def update(self, user_id: str, user: User) -> Optional[User]:
        user.updated_at = datetime.now()

        user_dict = user.to_dict()
        user_dict["password_hash"] = user.password_hash
        user_dict.pop("id", None)

        result = self._collection.update_one(
            {"_id": user_id},
            {"$set": user_dict}
        )

        if result.modified_count > 0 or result.matched_count > 0:
            user.id = user_id
            return user

        return None

    def delete(self, user_id: str) -> bool:
        result = self._collection.delete_one({"_id": user_id})
        return result.deleted_count > 0

    def activate(self, user_id: str) -> bool:
        result = self._collection.update_one(
            {"_id": user_id},
            {"$set": {"is_active": True, "updated_at": datetime.now().isoformat()}}
        )
        return result.modified_count > 0

    def deactivate(self, user_id: str) -> bool:
        result = self._collection.update_one(
            {"_id": user_id},
            {"$set": {"is_active": False, "updated_at": datetime.now().isoformat()}}
        )
        return result.modified_count > 0

    def _doc_to_entity(self, doc: dict) -> User:
        return User(
            id=doc["_id"],
            email=doc["email"],
            password_hash=doc["password_hash"],
            name=doc["name"],
            company_id=doc["company_id"],
            role_ids=doc.get("role_ids", []),
            is_active=doc.get("is_active", True),
            is_super_admin=doc.get("is_super_admin", False),
            created_at=User._parse_datetime(doc.get("created_at")),
            updated_at=User._parse_datetime(doc.get("updated_at"))
        )
