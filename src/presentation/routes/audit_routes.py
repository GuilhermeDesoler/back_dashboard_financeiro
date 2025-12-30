from flask import Blueprint, request, jsonify, g
from datetime import datetime
from src.database import get_shared_db
from src.infra.repositories import MongoAuditLogRepository
from src.application.middleware import require_auth, require_super_admin

audit_bp = Blueprint("audit", __name__)


@audit_bp.route("/admin/audit-logs", methods=["GET"])
@require_auth
@require_super_admin
def list_audit_logs():
    """
    Lista logs de auditoria (Super Admin only)

    Query params:
        user_id: Filtrar por usuário (opcional)
        company_id: Filtrar por empresa (opcional)
        action: Filtrar por ação (opcional)
        start_date: Data início (YYYY-MM-DD) (opcional)
        end_date: Data fim (YYYY-MM-DD) (opcional)
        limit: Limite de resultados (default: 100, max: 500)
        skip: Pular N registros (paginação)

    Returns:
        200: Lista de logs de auditoria
        403: Sem permissão (apenas super admin)
    """
    try:
        shared_db = get_shared_db()
        audit_repo = MongoAuditLogRepository(shared_db["audit_logs"])

        user_id = request.args.get("user_id")
        company_id = request.args.get("company_id")
        action = request.args.get("action")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")
        limit = min(int(request.args.get("limit", 100)), 500)
        skip = int(request.args.get("skip", 0))

        # Se tiver filtro de data
        if start_date_str and end_date_str:
            start_date = datetime.fromisoformat(start_date_str)
            end_date = datetime.fromisoformat(end_date_str)
            logs = audit_repo.find_by_date_range(
                start_date,
                end_date,
                user_id=user_id,
                company_id=company_id,
                limit=limit
            )
        # Filtro por usuário
        elif user_id:
            logs = audit_repo.find_by_user(user_id, limit=limit)
        # Filtro por empresa
        elif company_id:
            logs = audit_repo.find_by_company(company_id, limit=limit)
        # Filtro por ação
        elif action:
            logs = audit_repo.find_by_action(action, limit=limit)
        # Sem filtros - todos os logs
        else:
            logs = audit_repo.find_all(limit=limit, skip=skip)

        result = [log.to_dict() for log in logs]

        return jsonify({
            "total": len(result),
            "limit": limit,
            "skip": skip,
            "logs": result
        }), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
