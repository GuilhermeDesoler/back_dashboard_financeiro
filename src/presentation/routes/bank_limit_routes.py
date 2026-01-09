from flask import Blueprint, request, jsonify, g

from src.application.middleware.auth_bypass import require_auth, require_feature, require_role, require_super_admin
from src.application.use_cases import (
    CreateBankLimit,
    ListBankLimits,
    UpdateBankLimit,
    DeleteBankLimit,
)
from src.infra.repositories.mongo_bank_limit_repository import MongoBankLimitRepository
from src.database import get_tenant_db


bank_limit_bp = Blueprint("bank_limit", __name__)


def get_repository(company_id: str):
    """Retorna repositório do banco de dados da empresa"""
    tenant_db = get_tenant_db(company_id)
    bank_limit_collection = tenant_db["bank_limits"]
    return MongoBankLimitRepository(bank_limit_collection)


@bank_limit_bp.route("/bank-limits", methods=["POST"])
@require_auth
@require_feature("bank_limits.create")
def create_bank_limit():
    try:
        data = request.get_json()
        bank_name = data.get("bank_name")
        rotativo_available = float(data.get("rotativo_available", 0))
        rotativo_used = float(data.get("rotativo_used", 0))
        cheque_available = float(data.get("cheque_available", 0))
        cheque_used = float(data.get("cheque_used", 0))
        rotativo_rate = float(data.get("rotativo_rate", 0))
        cheque_rate = float(data.get("cheque_rate", 0))
        interest_rate = float(data.get("interest_rate", 0))

        repo = get_repository(g.company_id)
        use_case = CreateBankLimit(repo)
        bank_limit = use_case.execute(
            bank_name, rotativo_available, rotativo_used, cheque_available, cheque_used,
            rotativo_rate, cheque_rate, interest_rate
        )

        return jsonify(bank_limit.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@bank_limit_bp.route("/bank-limits", methods=["GET"])
@require_auth
@require_feature("bank_limits.read")
def list_bank_limits():
    try:
        repo = get_repository(g.company_id)
        use_case = ListBankLimits(repo)
        bank_limits = use_case.execute()

        return jsonify([limit.to_dict() for limit in bank_limits]), 200

    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@bank_limit_bp.route("/bank-limits/<limit_id>", methods=["PUT"])
@require_auth
@require_feature("bank_limits.update")
def update_bank_limit(limit_id: str):
    try:
        data = request.get_json()
        bank_name = data.get("bank_name")
        rotativo_available = float(data.get("rotativo_available", 0))
        rotativo_used = float(data.get("rotativo_used", 0))
        cheque_available = float(data.get("cheque_available", 0))
        cheque_used = float(data.get("cheque_used", 0))
        rotativo_rate = float(data.get("rotativo_rate", 0))
        cheque_rate = float(data.get("cheque_rate", 0))
        interest_rate = float(data.get("interest_rate", 0))

        repo = get_repository(g.company_id)
        use_case = UpdateBankLimit(repo)
        bank_limit = use_case.execute(
            limit_id, bank_name, rotativo_available, rotativo_used, cheque_available, cheque_used,
            rotativo_rate, cheque_rate, interest_rate
        )

        return jsonify(bank_limit.to_dict()), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@bank_limit_bp.route("/bank-limits/<limit_id>", methods=["DELETE"])
@require_auth
@require_feature("bank_limits.delete")
def delete_bank_limit(limit_id: str):
    try:
        repo = get_repository(g.company_id)
        use_case = DeleteBankLimit(repo)
        success = use_case.execute(limit_id)

        if success:
            return jsonify({"message": "Limite bancário excluído com sucesso"}), 200
        return jsonify({"error": "Falha ao excluir limite bancário"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500
