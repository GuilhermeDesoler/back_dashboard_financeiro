from flask import Blueprint, request, jsonify, g
from datetime import datetime

from src.application.middleware.auth_bypass import require_auth, require_feature, require_role, require_super_admin
from src.application.use_cases import CreateAccount, ListAccounts, DeleteAccount
from src.infra.repositories.mongo_account_repository import MongoAccountRepository
from src.database import get_tenant_db


account_bp = Blueprint("account", __name__)


def get_repository(company_id: str):
    """Retorna repositório do banco de dados da empresa"""
    tenant_db = get_tenant_db(company_id)
    account_collection = tenant_db["accounts"]
    return MongoAccountRepository(account_collection)


@account_bp.route("/accounts", methods=["POST"])
@require_auth
@require_feature("accounts.create")
def create_account():
    try:
        data = request.get_json()
        value = float(data.get("value"))
        date_str = data.get("date")
        description = data.get("description")
        account_type = data.get("type")

        date = datetime.fromisoformat(date_str)

        repo = get_repository(g.company_id)
        use_case = CreateAccount(repo)
        account = use_case.execute(value, date, description, account_type)

        return jsonify(account.to_dict()), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@account_bp.route("/accounts", methods=["GET"])
@require_auth
@require_feature("accounts.read")
def list_accounts():
    try:
        start_date_str = request.args.get("start_date")
        end_date_str = request.args.get("end_date")

        start_date = datetime.fromisoformat(start_date_str) if start_date_str else None
        end_date = datetime.fromisoformat(end_date_str) if end_date_str else None

        repo = get_repository(g.company_id)
        use_case = ListAccounts(repo)
        accounts = use_case.execute(start_date, end_date)

        return jsonify([account.to_dict() for account in accounts]), 200

    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@account_bp.route("/accounts/<account_id>", methods=["DELETE"])
@require_auth
@require_feature("accounts.delete")
def delete_account(account_id: str):
    try:
        repo = get_repository(g.company_id)
        use_case = DeleteAccount(repo)
        success = use_case.execute(account_id)

        if success:
            return jsonify({"message": "Conta excluída com sucesso"}), 200
        return jsonify({"error": "Falha ao excluir conta"}), 500

    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500
