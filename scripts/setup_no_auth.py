"""
Script simples para configurar o backend sem autenticação.
Cria um wrapper que injeta automaticamente o company_id.
"""

import sys
import os
from pathlib import Path

# Add project root and src to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

from src.database.mongo_connection import MongoConnection


def get_company_id():
    """Obtém o ID da empresa de teste"""
    db_connection = MongoConnection()
    shared_db = db_connection.shared_db
    company = shared_db['companies'].find_one({'name': 'Empresa Teste Ltda'})

    if not company:
        print("❌ Empresa de teste não encontrada!")
        return None

    return str(company['_id'])


def create_middleware_bypass():
    """Cria arquivo Python que sobrescreve os decoradores de autenticação"""

    company_id = get_company_id()
    if not company_id:
        return False

    middleware_file = project_root / 'src' / 'application' / 'middleware' / 'auth_bypass.py'

    content = f'''"""
Bypass de autenticação para desenvolvimento local.
Importar este módulo sobrescreverá os decoradores de autenticação.
"""

from flask import g
from functools import wraps

# Company ID fixo para modo sem autenticação
COMPANY_ID = "{company_id}"


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
'''

    with open(middleware_file, 'w') as f:
        f.write(content)

    print(f"✅ Arquivo criado: {middleware_file}")
    return True


def update_route_imports():
    """Atualiza os imports das rotas para usar o bypass"""

    routes_dir = project_root / 'src' / 'presentation' / 'routes'
    route_files = [
        'payment_modality_routes.py',
        'financial_entry_routes.py',
        'installment_routes.py',
        'account_routes.py',
        'bank_limit_routes.py',
        'platform_settings_routes.py',
    ]

    for route_file in route_files:
        filepath = routes_dir / route_file
        if not filepath.exists():
            continue

        with open(filepath, 'r') as f:
            content = f.read()

        # Substituir import
        old_import = 'from src.application.middleware import require_auth, require_feature'
        new_import = 'from src.application.middleware.auth_bypass import require_auth, require_feature, require_role, require_super_admin'

        if old_import in content:
            content = content.replace(old_import, new_import)

            with open(filepath, 'w') as f:
                f.write(content)

            print(f"✅ Atualizado: {route_file}")


def main():
    print("="*60)
    print("🔓 CONFIGURANDO BACKEND SEM AUTENTICAÇÃO")
    print("="*60)

    try:
        # Criar arquivo de bypass
        if not create_middleware_bypass():
            print("\n❌ Falha ao criar bypass")
            return

        # Atualizar imports das rotas
        print("\n📝 Atualizando imports das rotas...")
        update_route_imports()

        print("\n" + "="*60)
        print("✅ CONFIGURAÇÃO CONCLUÍDA!")
        print("="*60)
        print("\n⚠️  IMPORTANTE:")
        print("   • Reinicie o servidor Flask")
        print("   • Todas as requisições usarão a empresa: Empresa Teste Ltda")
        print("   • Modo de desenvolvimento - NÃO usar em produção")

    except Exception as e:
        print(f"\n❌ Erro: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
