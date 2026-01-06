"""
Script para remover restrições de autenticação das rotas da API.
A autenticação será gerenciada apenas no frontend.

Para executar: python scripts/remove_auth_restrictions.py
"""

import os
import re
from pathlib import Path

# Diretório das rotas
ROUTES_DIR = Path(__file__).parent.parent / 'src' / 'presentation' / 'routes'

# Arquivos de rotas para modificar (excluindo auth_routes.py que deve manter autenticação)
ROUTE_FILES = [
    'payment_modality_routes.py',
    'financial_entry_routes.py',
    'installment_routes.py',
    'account_routes.py',
    'bank_limit_routes.py',
    'platform_settings_routes.py',
]

# Company ID padrão para usar quando não houver autenticação
DEFAULT_COMPANY_ID = None  # Será obtido do banco


def get_default_company_id():
    """Obtém o ID da empresa de teste do banco de dados"""
    import sys
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / 'src'))

    from src.database.mongo_connection import MongoConnection

    db_connection = MongoConnection()
    shared_db = db_connection.shared_db
    company = shared_db['companies'].find_one({'name': 'Empresa Teste Ltda'})

    if not company:
        print("⚠️  Empresa de teste não encontrada! Execute seed_all.py primeiro.")
        return None

    return str(company['_id'])


def remove_decorators_from_file(file_path: Path):
    """Remove decoradores de autenticação de um arquivo de rotas"""
    print(f"\n📝 Processando: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content

    # Remover imports de middleware
    content = re.sub(
        r'from src\.application\.middleware import .*\n',
        '',
        content
    )

    # Remover decoradores @require_auth
    content = re.sub(
        r'@require_auth\n',
        '',
        content
    )

    # Remover decoradores @require_feature
    content = re.sub(
        r'@require_feature\([^)]+\)\n',
        '',
        content
    )

    # Remover decoradores @require_role
    content = re.sub(
        r'@require_role\([^)]+\)\n',
        '',
        content
    )

    # Remover decoradores @require_super_admin
    content = re.sub(
        r'@require_super_admin\n',
        '',
        content
    )

    # Substituir g.company_id por COMPANY_ID fixo
    # Primeiro, adicionar a constante no início do arquivo após os imports
    if 'COMPANY_ID = ' not in content:
        # Encontrar a última linha de import
        import_lines = []
        other_lines = []
        in_imports = True

        for line in content.split('\n'):
            if in_imports and (line.startswith('from ') or line.startswith('import ') or line.strip() == ''):
                import_lines.append(line)
            else:
                if line.strip() and in_imports:
                    in_imports = False
                other_lines.append(line)

        # Adicionar constante após imports
        import_lines.append('')
        import_lines.append('# Company ID padrão (sem autenticação)')
        import_lines.append('COMPANY_ID = None  # Será definido no startup')
        import_lines.append('')

        content = '\n'.join(import_lines + other_lines)

    # Substituir g.company_id por COMPANY_ID
    content = re.sub(r'g\.company_id', 'COMPANY_ID', content)

    # Salvar se houve mudanças
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"   ✅ Autenticação removida!")
        return True
    else:
        print(f"   ℹ️  Nenhuma mudança necessária")
        return False


def create_startup_script():
    """Cria script de inicialização que define o COMPANY_ID"""
    startup_content = '''"""
Configuração de inicialização para modo sem autenticação.
Define o COMPANY_ID padrão para todas as rotas.
"""

from src.database.mongo_connection import MongoConnection


def get_default_company_id():
    """Obtém o ID da empresa de teste"""
    db_connection = MongoConnection()
    shared_db = db_connection.shared_db
    company = shared_db['companies'].find_one({'name': 'Empresa Teste Ltda'})

    if not company:
        raise Exception("Empresa de teste não encontrada! Execute seed_all.py primeiro.")

    return str(company['_id'])


def initialize_company_id():
    """Inicializa o COMPANY_ID nas rotas"""
    company_id = get_default_company_id()

    # Importar e configurar todas as rotas
    from src.presentation.routes import (
        payment_modality_routes,
        financial_entry_routes,
        installment_routes,
        account_routes,
        bank_limit_routes,
        platform_settings_routes,
    )

    # Definir COMPANY_ID em cada módulo
    payment_modality_routes.COMPANY_ID = company_id
    financial_entry_routes.COMPANY_ID = company_id
    installment_routes.COMPANY_ID = company_id
    account_routes.COMPANY_ID = company_id
    bank_limit_routes.COMPANY_ID = company_id
    platform_settings_routes.COMPANY_ID = company_id

    print(f"✅ COMPANY_ID configurado: {company_id}")
    return company_id
'''

    init_file = ROUTES_DIR.parent.parent / 'startup_no_auth.py'
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(startup_content)

    print(f"\n📄 Arquivo de startup criado: {init_file}")


def update_main_app():
    """Atualiza o app principal para usar a configuração sem autenticação"""
    app_file = Path(__file__).parent.parent / 'src' / 'main.py'

    print(f"\n📝 Atualizando {app_file.name}...")

    with open(app_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Adicionar import e inicialização
    if 'from startup_no_auth import initialize_company_id' not in content:
        # Encontrar onde adicionar o import
        lines = content.split('\n')

        # Procurar pela criação do app
        for i, line in enumerate(lines):
            if 'def create_app' in line or 'app = Flask' in line:
                # Adicionar import antes da função/criação do app
                lines.insert(i, 'from startup_no_auth import initialize_company_id')
                lines.insert(i + 1, '')
                break

        content = '\n'.join(lines)

    # Adicionar inicialização após register blueprints
    if 'initialize_company_id()' not in content:
        lines = content.split('\n')

        # Procurar pelo último register_blueprint
        last_register_idx = -1
        for i, line in enumerate(lines):
            if 'register_blueprint' in line:
                last_register_idx = i

        if last_register_idx >= 0:
            # Adicionar após o último register_blueprint
            lines.insert(last_register_idx + 1, '')
            lines.insert(last_register_idx + 2, '    # Inicializar COMPANY_ID para modo sem autenticação')
            lines.insert(last_register_idx + 3, '    initialize_company_id()')
            lines.insert(last_register_idx + 4, '')

        content = '\n'.join(lines)

    with open(app_file, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"   ✅ main.py atualizado!")


def main():
    """Executa o processo de remoção de autenticação"""
    print("="*60)
    print("🔓 REMOVENDO RESTRIÇÕES DE AUTENTICAÇÃO DAS APIS")
    print("="*60)

    try:
        # Obter company ID padrão
        print("\n🔍 Buscando empresa de teste...")
        global DEFAULT_COMPANY_ID
        DEFAULT_COMPANY_ID = get_default_company_id()

        if not DEFAULT_COMPANY_ID:
            return

        print(f"   ✅ Empresa encontrada: {DEFAULT_COMPANY_ID}")

        # Confirmar ação
        response = input("\n⚠️  Isso removerá TODAS as restrições de autenticação. Continuar? (s/N): ")
        if response.lower() != 's':
            print("❌ Operação cancelada.")
            return

        # Processar cada arquivo de rotas
        modified_count = 0
        for filename in ROUTE_FILES:
            file_path = ROUTES_DIR / filename
            if file_path.exists():
                if remove_decorators_from_file(file_path):
                    modified_count += 1
            else:
                print(f"⚠️  Arquivo não encontrado: {filename}")

        # Criar script de startup
        create_startup_script()

        # Atualizar main.py
        update_main_app()

        print("\n" + "="*60)
        print("✅ RESTRIÇÕES DE AUTENTICAÇÃO REMOVIDAS COM SUCESSO!")
        print("="*60)
        print(f"\n📊 Resumo:")
        print(f"   • {modified_count} arquivos modificados")
        print(f"   • Company ID padrão: {DEFAULT_COMPANY_ID}")
        print(f"\n⚠️  IMPORTANTE:")
        print(f"   • Todas as rotas agora usam a empresa: Empresa Teste Ltda")
        print(f"   • A autenticação deve ser implementada no frontend")
        print(f"   • Reinicie o servidor Flask para aplicar as mudanças")

        print("\n🚀 Para aplicar as mudanças:")
        print("   1. Reinicie o servidor: python src/main.py")
        print("   2. Teste as rotas sem token de autenticação")

    except Exception as e:
        print(f"\n❌ Erro durante remoção: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
