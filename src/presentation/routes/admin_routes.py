from flask import Blueprint, request, jsonify, g
from src.database import get_shared_db, get_tenant_db
from src.infra.repositories import (
    MongoCompanyRepository,
    MongoUserRepository,
    MongoRoleRepository,
    MongoFeatureRepository
)
from src.application.use_cases import CreateCompany, ListCompanies
from src.application.use_cases.admin import ImpersonateCompany
from src.application.middleware import require_auth, require_super_admin
from src.infra.security import JWTHandler, PasswordHash
from src.domain.entities import User

admin_bp = Blueprint("admin", __name__)


def get_repositories():
    """Retorna repositórios do shared_db"""
    shared_db = get_shared_db()

    company_repo = MongoCompanyRepository(shared_db["companies"])
    user_repo = MongoUserRepository(shared_db["users"])
    feature_repo = MongoFeatureRepository(shared_db["features"])

    return company_repo, user_repo, feature_repo


# ========== EMPRESAS ==========

@admin_bp.route("/admin/companies", methods=["GET"])
@require_auth
@require_super_admin
def list_all_companies():
    """
    Lista todas as empresas (Super Admin only)
    Para uso em impersonate e gestão

    Query params:
        only_active: true|false (default: true)

    Returns:
        200: Lista de empresas com estatísticas
        403: Sem permissão (apenas super admin)
    """
    try:
        only_active = request.args.get("only_active", "true").lower() == "true"

        company_repo, user_repo, _ = get_repositories()
        use_case = ListCompanies(company_repo)
        companies = use_case.execute(only_active=only_active)

        # Adiciona contagem de usuários por empresa
        result = []
        for company in companies:
            users = user_repo.find_by_company(company.id)
            company_dict = company.to_dict()
            company_dict["users_count"] = len(users)
            result.append(company_dict)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@admin_bp.route("/admin/companies", methods=["POST"])
@require_auth
@require_super_admin
def create_new_company():
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

        company_repo, _, _ = get_repositories()
        use_case = CreateCompany(company_repo)
        company = use_case.execute(name, cnpj, phone, plan)

        return jsonify({
            "message": "Empresa criada com sucesso",
            "company": company.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@admin_bp.route("/admin/companies/<company_id>", methods=["GET"])
@require_auth
@require_super_admin
def get_company_details(company_id):
    """
    Obtém detalhes de uma empresa específica (Super Admin only)

    Returns:
        200: Detalhes da empresa com estatísticas
        404: Empresa não encontrada
        403: Sem permissão (apenas super admin)
    """
    try:
        company_repo, user_repo, _ = get_repositories()

        company = company_repo.find_by_id(company_id)
        if not company:
            return jsonify({"error": "Empresa não encontrada"}), 404

        # Busca usuários da empresa
        users = user_repo.find_by_company(company_id)

        # Busca roles da empresa
        tenant_db = get_tenant_db(company_id)
        role_repo = MongoRoleRepository(tenant_db["roles"])

        result = company.to_dict()
        result["users_count"] = len(users)
        result["users"] = [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "is_active": u.is_active,
                "is_super_admin": u.is_super_admin
            }
            for u in users
        ]

        return jsonify(result), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


# ========== IMPERSONATE ==========

@admin_bp.route("/admin/impersonate/<company_id>", methods=["POST"])
@require_auth
@require_super_admin
def impersonate_company(company_id):
    """
    Gera token para impersonate de uma empresa (Super Admin only)
    O token gerado permite acesso total aos dados da empresa

    Returns:
        200: Token de impersonate gerado
        404: Empresa não encontrada
        403: Sem permissão (apenas super admin)
    """
    try:
        company_repo, user_repo, feature_repo = get_repositories()

        # Busca role repository da empresa alvo (para futuro uso)
        tenant_db = get_tenant_db(company_id)
        role_repo = MongoRoleRepository(tenant_db["roles"])

        jwt_handler = JWTHandler()

        use_case = ImpersonateCompany(
            company_repo,
            user_repo,
            role_repo,
            feature_repo,
            jwt_handler
        )

        result = use_case.execute(g.user_id, company_id)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


# ========== USUÁRIOS ==========

@admin_bp.route("/admin/users", methods=["GET"])
@require_auth
@require_super_admin
def list_all_users():
    """
    Lista todos os usuários do sistema (Super Admin only)

    Query params:
        company_id: Filtrar por empresa (opcional)
        only_active: true|false (default: true)

    Returns:
        200: Lista de usuários
        403: Sem permissão (apenas super admin)
    """
    try:
        company_id = request.args.get("company_id")
        only_active = request.args.get("only_active", "true").lower() == "true"

        _, user_repo, _ = get_repositories()

        if company_id:
            users = user_repo.find_by_company(company_id)
        else:
            users = user_repo.find_all()

        if only_active:
            users = [u for u in users if u.is_active]

        result = [
            {
                "id": u.id,
                "name": u.name,
                "email": u.email,
                "company_id": u.company_id,
                "is_active": u.is_active,
                "is_super_admin": u.is_super_admin,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in users
        ]

        return jsonify(result), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@admin_bp.route("/admin/users", methods=["POST"])
@require_auth
@require_super_admin
def create_user():
    """
    Cria um novo usuário (Super Admin only)

    Body:
        {
            "email": "user@example.com",
            "password": "senha123",
            "name": "Nome do Usuário",
            "company_id": "company-uuid",
            "is_super_admin": false (opcional)
        }

    Returns:
        201: Usuário criado com sucesso
        400: Erro de validação
        403: Sem permissão (apenas super admin)
    """
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")
        name = data.get("name")
        company_id = data.get("company_id")
        is_super_admin = data.get("is_super_admin", False)

        # Validações
        if not email or not email.strip():
            raise ValueError("Email é obrigatório")

        if not password or len(password) < 6:
            raise ValueError("Senha deve ter no mínimo 6 caracteres")

        if not name or not name.strip():
            raise ValueError("Nome é obrigatório")

        if not company_id or not company_id.strip():
            raise ValueError("company_id é obrigatório")

        company_repo, user_repo, _ = get_repositories()

        # Verifica se email já existe
        existing_user = user_repo.find_by_email(email)
        if existing_user:
            raise ValueError("Email já cadastrado")

        # Verifica se empresa existe
        company = company_repo.find_by_id(company_id)
        if not company:
            raise ValueError("Empresa não encontrada")

        # Cria usuário
        password_hash = PasswordHash.hash(password)

        user = User(
            email=email.strip().lower(),
            password_hash=password_hash,
            name=name.strip(),
            company_id=company_id,
            role_ids=[],
            is_active=True,
            is_super_admin=is_super_admin
        )

        created_user = user_repo.create(user)

        return jsonify({
            "message": "Usuário criado com sucesso",
            "user": created_user.to_dict()
        }), 201

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


@admin_bp.route("/admin/users/<user_id>/toggle-active", methods=["PATCH"])
@require_auth
@require_super_admin
def toggle_user_active(user_id):
    """
    Ativa/Desativa um usuário (Super Admin only)

    Body:
        {
            "activate": true|false
        }

    Returns:
        200: Usuário atualizado
        404: Usuário não encontrado
        403: Sem permissão (apenas super admin)
    """
    try:
        data = request.get_json()
        activate = data.get("activate", True)

        _, user_repo, _ = get_repositories()

        user = user_repo.find_by_id(user_id)
        if not user:
            return jsonify({"error": "Usuário não encontrado"}), 404

        if activate:
            user_repo.activate(user_id)
            message = "Usuário ativado com sucesso"
        else:
            user_repo.deactivate(user_id)
            message = "Usuário desativado com sucesso"

        return jsonify({"message": message}), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500


# ========== DASHBOARD / ESTATÍSTICAS ==========

@admin_bp.route("/admin/dashboard", methods=["GET"])
@require_auth
@require_super_admin
def admin_dashboard():
    """
    Retorna estatísticas gerais do sistema (Super Admin only)

    Returns:
        200: Estatísticas do sistema
        403: Sem permissão (apenas super admin)
    """
    try:
        company_repo, user_repo, feature_repo = get_repositories()

        # Estatísticas de empresas
        all_companies = company_repo.find_all()
        active_companies = [c for c in all_companies if c.is_active]

        # Estatísticas de usuários
        all_users = user_repo.find_all()
        active_users = [u for u in all_users if u.is_active]
        super_admins = [u for u in all_users if u.is_super_admin]

        # Estatísticas de features
        all_features = feature_repo.find_all()

        # Empresas por plano
        plans_count = {}
        for company in all_companies:
            plan = company.plan
            plans_count[plan] = plans_count.get(plan, 0) + 1

        result = {
            "companies": {
                "total": len(all_companies),
                "active": len(active_companies),
                "inactive": len(all_companies) - len(active_companies),
                "by_plan": plans_count
            },
            "users": {
                "total": len(all_users),
                "active": len(active_users),
                "inactive": len(all_users) - len(active_users),
                "super_admins": len(super_admins)
            },
            "features": {
                "total": len(all_features)
            }
        }

        return jsonify(result), 200

    except Exception:
        return jsonify({"error": "Erro interno do servidor"}), 500
