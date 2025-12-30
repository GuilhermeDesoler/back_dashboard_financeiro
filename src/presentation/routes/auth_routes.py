from flask import Blueprint, request, jsonify
from src.database import get_shared_db
from src.infra.repositories import (
    MongoUserRepository,
    MongoCompanyRepository,
    MongoRoleRepository,
    MongoFeatureRepository
)
from src.infra.security import JWTHandler
from src.application.use_cases.auth import Login, RefreshToken

auth_bp = Blueprint("auth", __name__)


def get_auth_repositories():
    """Retorna repositórios do shared_db para autenticação"""
    shared_db = get_shared_db()

    user_repo = MongoUserRepository(shared_db["users"])
    company_repo = MongoCompanyRepository(shared_db["companies"])
    role_repo = MongoRoleRepository(shared_db["roles"])
    feature_repo = MongoFeatureRepository(shared_db["features"])

    return user_repo, company_repo, role_repo, feature_repo


@auth_bp.route("/auth/login", methods=["POST"])
def login():
    """
    Autentica um usuário

    Body:
        {
            "email": "user@example.com",
            "password": "senha123"
        }

    Returns:
        200: Login bem-sucedido com token
        400: Credenciais inválidas
    """
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        user_repo, _, role_repo, feature_repo = get_auth_repositories()
        jwt_handler = JWTHandler()

        use_case = Login(user_repo, role_repo, feature_repo, jwt_handler)
        result = use_case.execute(email, password)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@auth_bp.route("/auth/refresh", methods=["POST"])
def refresh():
    """
    Renova o token de acesso usando refresh token

    Body:
        {
            "refresh_token": "refresh_token_jwt"
        }

    Returns:
        200: Novos tokens gerados
        400: Refresh token inválido
    """
    try:
        data = request.get_json()
        refresh_token = data.get("refresh_token")

        if not refresh_token:
            raise ValueError("Refresh token é obrigatório")

        user_repo, _, role_repo, feature_repo = get_auth_repositories()
        jwt_handler = JWTHandler()

        use_case = RefreshToken(user_repo, role_repo, feature_repo, jwt_handler)
        result = use_case.execute(refresh_token)

        return jsonify(result), 200

    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Erro interno do servidor"}), 500


@auth_bp.route("/auth/me", methods=["GET"])
def me():
    """
    Retorna informações do usuário autenticado

    Headers:
        Authorization: Bearer <token>

    Returns:
        200: Dados do usuário
        401: Não autenticado
    """
    from src.application.middleware import require_auth
    from flask import g

    @require_auth
    def get_user_info():
        return jsonify({
            "user_id": g.user_id,
            "email": g.email,
            "name": g.name,
            "company_id": g.company_id,
            "roles": g.roles,
            "features": g.features
        }), 200

    return get_user_info()
