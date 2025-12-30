from typing import List, Optional
from datetime import datetime
from uuid import uuid4
from pymongo.collection import Collection

from src.domain.entities import Company
from src.domain.repositories import CompanyRepository


class MongoCompanyRepository(CompanyRepository):
    def __init__(self, collection: Collection):
        self._collection = collection

    def create(self, company: Company) -> Company:
        company.id = str(uuid4())
        company.created_at = datetime.now()
        company.updated_at = datetime.now()

        company_dict = company.to_dict()
        company_dict["_id"] = company.id
        company_dict.pop("id")

        self._collection.insert_one(company_dict)

        return company

    def find_by_id(self, company_id: str) -> Optional[Company]:
        doc = self._collection.find_one({"_id": company_id})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_by_cnpj(self, cnpj: str) -> Optional[Company]:
        doc = self._collection.find_one({"cnpj": cnpj})
        if doc:
            return self._doc_to_entity(doc)
        return None

    def find_all(self) -> List[Company]:
        docs = self._collection.find()
        return [self._doc_to_entity(doc) for doc in docs]

    def update(self, company_id: str, company: Company) -> Optional[Company]:
        company.updated_at = datetime.now()

        company_dict = company.to_dict()
        company_dict.pop("id", None)

        result = self._collection.update_one(
            {"_id": company_id},
            {"$set": company_dict}
        )

        if result.modified_count > 0 or result.matched_count > 0:
            company.id = company_id
            return company

        return None

    def delete(self, company_id: str) -> bool:
        result = self._collection.delete_one({"_id": company_id})
        return result.deleted_count > 0

    def _doc_to_entity(self, doc: dict) -> Company:
        return Company(
            id=doc["_id"],
            name=doc["name"],
            cnpj=doc["cnpj"],
            phone=doc.get("phone", ""),
            plan=doc.get("plan", "basic"),
            is_active=doc.get("is_active", True),
            settings=doc.get("settings", {"timezone": "America/Sao_Paulo", "currency": "BRL"}),
            created_at=Company._parse_datetime(doc.get("created_at")),
            updated_at=Company._parse_datetime(doc.get("updated_at"))
        )
