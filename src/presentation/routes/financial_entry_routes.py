from flask import Blueprint, request, jsonify, g
from datetime import datetime
from src.database import get_tenant_db
from src.infra.repositories import (
    MongoFinancialEntryRepository,
    MongoPaymentModalityRepository,
)
from src.application.use_cases import (
    CreateFinancialEntry,
    ListFinancialEntries,
    UpdateFinancialEntry,
    DeleteFinancialEntry,
)
from src.application.middleware import require_auth, require_feature

financial_entry_bp = Blueprint("financial_entries", __name__)


def get_repositories(company_id: str):
    """Retorna repositórios do banco de dados da empresa"""
    tenant_db = get_tenant_db(company_id)

    entry_collection = tenant_db["financial_entries"]
    modality_collection = tenant_db["payment_modalities"]

    entry_repo = MongoFinancialEntryRepository(entry_collection)
    modality_repo = MongoPaymentModalityRepository(modality_collection)

    return entry_repo, modality_repo


@financial_entry_bp.route("/financial-entries", methods=["POST"])
@require_auth
@require_feature("financial_entries.create")
def create_entry():
    try:
        data = request.get_json()
        value = float(data.get("value"))
        date_str = data.get("date")
        modality_id = data.get("modality_id")
        
        date = datetime.fromisoformat(date_str)

        # Usa o DB da empresa do usuário autenticado
        entry_repo, modality_repo = get_repositories(g.company_id)
        use_case = CreateFinancialEntry(entry_repo, modality_repo)
        entry = use_case.execute(value, date, modality_id)
        
        return jsonify(entry.to_dict()), 201
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@financial_entry_bp.route("/financial-entries", methods=["GET"])
@require_auth
@require_feature("financial_entries.read")
def list_entries():
    try:
        modality_id = request.args.get("modality_id")
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        # Usa o DB da empresa do usuário autenticado
        entry_repo, _ = get_repositories(g.company_id)
        use_case = ListFinancialEntries(entry_repo)
        entries = use_case.execute(modality_id, start_date, end_date)

        return jsonify([e.to_dict() for e in entries]), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@financial_entry_bp.route("/financial-entries/<entry_id>", methods=["GET"])
@require_auth
@require_feature("financial_entries.read")
def get_entry_by_id(entry_id):
    """
    Busca um lançamento financeiro por ID

    Returns:
        200: Lançamento encontrado
        404: Lançamento não encontrado
    """
    try:
        # Usa o DB da empresa do usuário autenticado
        entry_repo, _ = get_repositories(g.company_id)

        entry = entry_repo.find_by_id(entry_id)
        if not entry:
            return jsonify({"error": "Lançamento não encontrado"}), 404

        return jsonify(entry.to_dict()), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@financial_entry_bp.route("/financial-entries/<entry_id>", methods=["PUT"])
@require_auth
@require_feature("financial_entries.update")
def update_entry(entry_id):
    try:
        data = request.get_json()
        value = float(data.get("value"))
        date_str = data.get("date")
        modality_id = data.get("modality_id")
        
        date = datetime.fromisoformat(date_str)

        # Usa o DB da empresa do usuário autenticado
        entry_repo, modality_repo = get_repositories(g.company_id)
        use_case = UpdateFinancialEntry(entry_repo, modality_repo)
        entry = use_case.execute(entry_id, value, date, modality_id)
        
        return jsonify(entry.to_dict()), 200
    
    except ValueError as e:
        return jsonify({"error": str(e)}), 404 if "não encontrado" in str(e) else 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@financial_entry_bp.route("/financial-entries/<entry_id>", methods=["DELETE"])
@require_auth
@require_feature("financial_entries.delete")
def delete_entry(entry_id):
    try:
        # Usa o DB da empresa do usuário autenticado
        entry_repo, _ = get_repositories(g.company_id)
        use_case = DeleteFinancialEntry(entry_repo)
        success = use_case.execute(entry_id)

        if success:
            return jsonify({"message": "Lançamento deletado com sucesso"}), 200
        return jsonify({"error": "Erro ao deletar lançamento"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
