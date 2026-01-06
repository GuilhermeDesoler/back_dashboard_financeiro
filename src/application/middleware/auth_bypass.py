"""
Bypass de autenticação para desenvolvimento local.
Importar este módulo sobrescreverá os decoradores de autenticação.
"""

from flask import g
from functools import wraps

# Company ID fixo para modo sem autenticação
COMPANY_ID = "03a24d1f-52fa-429f-9a1c-1b4fc4a9f268"


def no_auth_decorator(f):
    """Decorator que não faz nada, apenas injeta company_id"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Inject company_id into g object
        g.company_id = COMPANY_ID
        g.user_id = "bypass-user"
        g.email = "teste@teste.com"
        g.is_super_admin = True
        g.roles = ["Admin"]
        g.features = []
        return f(*args, **kwargs)
    return wrapper


# Sobrescrever decoradores
require_auth = no_auth_decorator
require_feature = lambda feature: no_auth_decorator
require_role = lambda role: no_auth_decorator
require_super_admin = no_auth_decorator


print("⚠️  Auth bypass ativado - COMPANY_ID:", COMPANY_ID)
