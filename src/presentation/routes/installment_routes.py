from flask import Blueprint, request, jsonify, g
from datetime import datetime
from src.database import get_tenant_db
from src.infra.repositories import (
    MongoInstallmentRepository,
    MongoFinancialEntryRepository,
)
from src.application.use_cases import (
    ListInstallments,
    PayInstallment,
    UnpayInstallment,
    GetDailyCreditSummary,
)
from src.application.middleware.auth_bypass import require_auth, require_feature, require_role, require_super_admin

installment_bp = Blueprint("installments", __name__)


def get_repositories(company_id: str):
    """Retorna repositórios do banco de dados da empresa"""
    tenant_db = get_tenant_db(company_id)

    installment_collection = tenant_db["installments"]
    entry_collection = tenant_db["financial_entries"]

    installment_repo = MongoInstallmentRepository(installment_collection)
    entry_repo = MongoFinancialEntryRepository(entry_collection)

    return installment_repo, entry_repo


@installment_bp.route("/installments", methods=["GET"])
@require_auth
@require_feature("financial_entries.read")
def list_installments():
    """
    Lista parcelas de crediário

    Query params:
        financial_entry_id: Filtrar por lançamento financeiro (opcional)
    """
    try:
        financial_entry_id = request.args.get("financial_entry_id")

        installment_repo, _ = get_repositories(g.company_id)
        use_case = ListInstallments(installment_repo)
        installments = use_case.execute(financial_entry_id)

        return jsonify([inst.to_dict() for inst in installments]), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@installment_bp.route("/installments/<installment_id>/pay", methods=["PATCH"])
@require_auth
@require_feature("financial_entries.update")
def pay_installment(installment_id):
    """Marca uma parcela como paga"""
    try:
        data = request.get_json() or {}
        payment_date_str = data.get("payment_date")

        payment_date = None
        if payment_date_str:
            payment_date = datetime.fromisoformat(payment_date_str)

        installment_repo, _ = get_repositories(g.company_id)
        use_case = PayInstallment(installment_repo)
        installment = use_case.execute(installment_id, payment_date)

        return jsonify(installment.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@installment_bp.route("/installments/<installment_id>/unpay", methods=["PATCH"])
@require_auth
@require_feature("financial_entries.update")
def unpay_installment(installment_id):
    """Marca uma parcela como não paga"""
    try:
        installment_repo, _ = get_repositories(g.company_id)
        use_case = UnpayInstallment(installment_repo)
        installment = use_case.execute(installment_id)

        return jsonify(installment.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@installment_bp.route("/installments/daily-summary", methods=["GET"])
@require_auth
@require_feature("financial_entries.read")
def get_daily_credit_summary():
    """
    Retorna resumo diário do crediário

    Query params:
        start_date: Data inicial (formato ISO, opcional)
        end_date: Data final (formato ISO, opcional)

    Returns:
        Lista de resumos diários com:
        - date: Data do resumo
        - total_receivable: Total a receber (parcelas não pagas com vencimento naquele dia)
        - total_received: Total recebido (pagamentos de crediário naquele dia)
        - difference: Diferença (recebido - a receber)
    """
    try:
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        installment_repo, entry_repo = get_repositories(g.company_id)
        use_case = GetDailyCreditSummary(installment_repo, entry_repo)
        summary = use_case.execute(start_date, end_date)

        return jsonify(summary), 200

    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500
