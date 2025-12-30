from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class AuditLog:
    """
    Entidade de Log de Auditoria

    Registra todas as ações importantes no sistema para rastreabilidade.
    """
    action: str  # Ação realizada (ex: "create_company", "delete_user", "impersonate")
    user_id: str  # ID do usuário que realizou a ação
    user_email: str  # Email do usuário
    company_id: Optional[str]  # ID da empresa afetada (se aplicável)
    target_type: Optional[str]  # Tipo do alvo (ex: "company", "user", "financial_entry")
    target_id: Optional[str]  # ID do alvo
    details: Dict[str, Any] = field(default_factory=dict)  # Detalhes adicionais
    ip_address: Optional[str] = None  # IP de onde veio a requisição
    user_agent: Optional[str] = None  # User agent do navegador
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Converte a entidade para dicionário"""
        return {
            "id": self.id,
            "action": self.action,
            "user_id": self.user_id,
            "user_email": self.user_email,
            "company_id": self.company_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "details": self.details,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'AuditLog':
        """Cria entidade a partir de dicionário"""
        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))

        return AuditLog(
            id=data.get("id", str(uuid.uuid4())),
            action=data["action"],
            user_id=data["user_id"],
            user_email=data["user_email"],
            company_id=data.get("company_id"),
            target_type=data.get("target_type"),
            target_id=data.get("target_id"),
            details=data.get("details", {}),
            ip_address=data.get("ip_address"),
            user_agent=data.get("user_agent"),
            created_at=created_at or datetime.utcnow()
        )
