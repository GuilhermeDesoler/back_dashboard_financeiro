from functools import wraps
from flask import request, jsonify, g
from src.infra.security import JWTHandler


def require_auth(f):
    """
    Decorator que exige autenticação via JWT token

    Usage:
        @require_auth
        def my_route():
            user_id = g.user_id
            company_id = g.company_id
            ...

    O token deve ser enviado no header:
        Authorization: Bearer <token>
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token or not token.startswith('Bearer '):
            return jsonify({"error": "Token não fornecido"}), 401

        try:
            token = token.replace('Bearer ', '')
            jwt_handler = JWTHandler()
            payload = jwt_handler.verify_token(token)

            # Armazena dados do usuário no contexto da requisição
            g.user_id = payload.get('user_id')
            g.email = payload.get('email')
            g.name = payload.get('name')
            g.company_id = payload.get('company_id')
            g.roles = payload.get('roles', [])
            g.features = payload.get('features', [])
            g.is_super_admin = payload.get('is_super_admin', False)

            if not g.user_id:
                return jsonify({"error": "Token inválido"}), 401

            return f(*args, **kwargs)

        except ValueError as e:
            return jsonify({"error": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "Erro ao processar token"}), 500

    return decorated_function


def require_feature(feature_code: str):
    """
    Decorator que exige uma feature específica
    Super admins têm bypass automático

    Usage:
        @require_auth
        @require_feature("financial_entries.create")
        def create_entry():
            ...

    Deve ser usado APÓS @require_auth
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'features'):
                return jsonify({"error": "Usuário não autenticado"}), 401

            # Super admin tem acesso a tudo
            if g.get('is_super_admin', False):
                return f(*args, **kwargs)

            if feature_code not in g.features:
                return jsonify({
                    "error": "Acesso negado",
                    "message": f"Feature '{feature_code}' não disponível para este usuário"
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_role(role_name: str):
    """
    Decorator que exige uma role específica

    Usage:
        @require_auth
        @require_role("Admin")
        def admin_route():
            ...

    Deve ser usado APÓS @require_auth
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not hasattr(g, 'roles'):
                return jsonify({"error": "Usuário não autenticado"}), 401

            if role_name not in g.roles:
                return jsonify({
                    "error": "Acesso negado",
                    "message": f"Role '{role_name}' necessária"
                }), 403

            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_super_admin(f):
    """
    Decorator que exige super admin

    Usage:
        @require_auth
        @require_super_admin
        def super_admin_route():
            ...

    Deve ser usado APÓS @require_auth
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not hasattr(g, 'is_super_admin'):
            return jsonify({"error": "Usuário não autenticado"}), 401

        if not g.is_super_admin:
            return jsonify({
                "error": "Acesso negado",
                "message": "Apenas super administradores podem acessar"
            }), 403

        return f(*args, **kwargs)
    return decorated_function
