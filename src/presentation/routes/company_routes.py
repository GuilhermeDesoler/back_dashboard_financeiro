from flask import Blueprint, request, jsonify
from src.database import get_shared_db
from src.infra.repositories import MongoCompanyRepository
from src.application.use_cases import CreateCompany, ListCompanies
from src.application.middleware import require_auth, require_feature, require_super_admin

company_bp = Blueprint("companies", __name__)


def get_repository():
    """Retorna repositório do shared_db para companies"""
    shared_db = get_shared_db()
    return MongoCompanyRepository(shared_db["companies"])


@company_bp.route("/companies", methods=["POST"])
@require_auth
@require_super_admin
def create_company():
    """
    Cria uma nova empresa (Super Admin only)

    Body:
        {
            "name": "Nome da Empresa",
            "cnpj": "12.345.678/0001-90",
            "phone": "(11) 99999-9999",
            "plan": "basic"
        }

    Returns:
        201: Empresa criada com sucesso
        400: Erro de validação
        403: Sem permissão (apenas super admin)
    """
    try:
        data = request.get_json()

        name = data.get("name")
        cnpj = data.get("cnpj")
        phone = data.get("phone")
        plan = data.get("plan", "basic")

        repository = get_repository()
        use_case = CreateCompany(repository)
        company = use_case.execute(name, cnpj, phone, plan)

        return jsonify({
            "message": "Empresa criada com sucesso",
            "company": company.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@company_bp.route("/companies", methods=["GET"])
@require_auth
@require_super_admin
def list_companies():
    """
    Lista todas as empresas (Super Admin only)
    Para uso em impersonate no frontend

    Query params:
        only_active: true|false (default: true)

    Returns:
        200: Lista de empresas
        403: Sem permissão (apenas super admin)
    """
    try:
        only_active = request.args.get("only_active", "true").lower() == "true"

        repository = get_repository()
        use_case = ListCompanies(repository)
        companies = use_case.execute(only_active=only_active)

        return jsonify([c.to_dict() for c in companies]), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
