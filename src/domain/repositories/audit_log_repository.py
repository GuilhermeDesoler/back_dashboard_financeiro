from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from src.domain.entities.audit_log import AuditLog


class AuditLogRepository(ABC):
    """Interface do repositório de logs de auditoria"""

    @abstractmethod
    def create(self, audit_log: AuditLog) -> AuditLog:
        """Cria um novo log de auditoria"""
        pass

    @abstractmethod
    def find_by_user(self, user_id: str, limit: int = 100) -> List[AuditLog]:
        """Busca logs por usuário"""
        pass

    @abstractmethod
    def find_by_company(self, company_id: str, limit: int = 100) -> List[AuditLog]:
        """Busca logs por empresa"""
        pass

    @abstractmethod
    def find_by_action(self, action: str, limit: int = 100) -> List[AuditLog]:
        """Busca logs por ação"""
        pass

    @abstractmethod
    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        user_id: Optional[str] = None,
        company_id: Optional[str] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Busca logs por período"""
        pass

    @abstractmethod
    def find_all(self, limit: int = 100, skip: int = 0) -> List[AuditLog]:
        """Busca todos os logs (paginado)"""
        pass
