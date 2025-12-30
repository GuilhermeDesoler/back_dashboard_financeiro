from typing import Optional, Dict, Any
from flask import request, g
from src.domain.entities.audit_log import AuditLog
from src.domain.repositories.audit_log_repository import AuditLogRepository


class AuditService:
    """
    Serviço de Auditoria

    Facilita a criação de logs de auditoria em todo o sistema.
    """

    def __init__(self, audit_log_repository: AuditLogRepository):
        self._repository = audit_log_repository

    def log(
        self,
        action: str,
        user_id: str,
        user_email: str,
        company_id: Optional[str] = None,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Cria um log de auditoria

        Args:
            action: Ação realizada (ex: "create_company", "delete_user")
            user_id: ID do usuário que realizou a ação
            user_email: Email do usuário
            company_id: ID da empresa afetada
            target_type: Tipo do alvo (ex: "company", "user")
            target_id: ID do alvo
            details: Detalhes adicionais

        Returns:
            AuditLog criado
        """
        # Tenta capturar IP e user agent da requisição (se disponível)
        ip_address = None
        user_agent = None

        try:
            if request:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent')
        except:
            pass  # Fora de contexto de requisição

        audit_log = AuditLog(
            action=action,
            user_id=user_id,
            user_email=user_email,
            company_id=company_id,
            target_type=target_type,
            target_id=target_id,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )

        return self._repository.create(audit_log)

    def log_from_context(
        self,
        action: str,
        target_type: Optional[str] = None,
        target_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> Optional[AuditLog]:
        """
        Cria um log usando dados do contexto Flask (g)

        Args:
            action: Ação realizada
            target_type: Tipo do alvo
            target_id: ID do alvo
            details: Detalhes adicionais

        Returns:
            AuditLog criado ou None se não houver contexto
        """
        try:
            if not hasattr(g, 'user_id') or not hasattr(g, 'email'):
                return None

            return self.log(
                action=action,
                user_id=g.user_id,
                user_email=g.email,
                company_id=getattr(g, 'company_id', None),
                target_type=target_type,
                target_id=target_id,
                details=details
            )
        except:
            return None
