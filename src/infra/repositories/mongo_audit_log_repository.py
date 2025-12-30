from typing import List, Optional
from datetime import datetime
from pymongo.collection import Collection
from src.domain.entities.audit_log import AuditLog
from src.domain.repositories.audit_log_repository import AuditLogRepository


class MongoAuditLogRepository(AuditLogRepository):
    """Implementação MongoDB do repositório de logs de auditoria"""

    def __init__(self, collection: Collection):
        self._collection = collection
        self._create_indexes()

    def _create_indexes(self):
        """Cria índices para otimizar consultas"""
        self._collection.create_index("user_id")
        self._collection.create_index("company_id")
        self._collection.create_index("action")
        self._collection.create_index("created_at")
        self._collection.create_index([("created_at", -1)])  # Ordenação descendente

    def create(self, audit_log: AuditLog) -> AuditLog:
        """Cria um novo log de auditoria"""
        log_dict = audit_log.to_dict()
        self._collection.insert_one(log_dict)
        return audit_log

    def find_by_user(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        """Busca logs por usuário"""
        cursor = self._collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit)

        return [AuditLog.from_dict(doc) for doc in cursor]

    def find_by_company(self, company_id: str, limit: int = 100) -> List[AuditLog]:
        """Busca logs por empresa"""
        cursor = self._collection.find(
            {"company_id": company_id}
        ).sort("created_at", -1).limit(limit)

        return [AuditLog.from_dict(doc) for doc in cursor]

    def find_by_action(self, action: str, limit: int = 100) -> List[AuditLog]:
        """Busca logs por ação"""
        cursor = self._collection.find(
            {"action": action}
        ).sort("created_at", -1).limit(limit)

        return [AuditLog.from_dict(doc) for doc in cursor]

    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None,
        company_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Busca logs por período"""
        query = {
            "created_at": {
                "$gte": start_date,
                "$lte": end_date
            }
        }

        if user_id:
            query["user_id"] = user_id

        if company_id:
            query["company_id"] = company_id

        cursor = self._collection.find(query).sort("created_at", -1).limit(limit)

        return [AuditLog.from_dict(doc) for doc in cursor]

    def find_all(self, limit: int = 100, skip: int = 0) -> List[AuditLog]:
        """Busca todos os logs (paginado)"""
        cursor = self._collection.find().sort("created_at", -1).skip(skip).limit(limit)

        return [AuditLog.from_dict(doc) for doc in cursor]
