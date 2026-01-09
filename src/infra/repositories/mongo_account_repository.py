from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from pymongo.collection import Collection

from src.domain.entities import Account
from src.domain.repositories import AccountRepository


class MongoAccountRepository(AccountRepository):
    def __init__(self, collection: Collection):
        self._collection = collection

    def create(self, account: Account) -> Account:
        account.id = str(uuid4())
        account.created_at = datetime.now()
        account.updated_at = datetime.now()

        account_dict = account.to_dict()
        account_dict['_id'] = account.id
        account_dict.pop('id')

        self._collection.insert_one(account_dict)

        return account

    def find_by_id(self, account_id: str) -> Optional[Account]:
        doc = self._collection.find_one({"_id": account_id})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_all(self) -> List[Account]:
        docs = self._collection.find().sort("date", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def find_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[Account]:
        docs = self._collection.find({
            "date": {
                "$gte": start_date.isoformat(),
                "$lte": end_date.isoformat()
            }
        }).sort("date", -1)
        return [self._doc_to_entity(doc) for doc in docs]

    def update(self, account: Account) -> Account:
        account.updated_at = datetime.now()

        account_dict = account.to_dict()
        account_dict["_id"] = account.id
        account_dict.pop("id")

        self._collection.update_one(
            {"_id": account.id},
            {"$set": account_dict}
        )

        return account

    def delete(self, account_id: str) -> bool:
        result = self._collection.delete_one({"_id": account_id})
        return result.deleted_count > 0

    def _doc_to_entity(self, doc: dict) -> Account:
        return Account(
            id=doc["_id"],
            value=doc["value"],
            date=Account._parse_datetime(doc["date"]),
            description=doc["description"],
            type=doc["type"],
            paid=doc.get("paid", False),
            created_at=Account._parse_datetime(doc.get("created_at")),
            updated_at=Account._parse_datetime(doc.get("updated_at"))
        )
