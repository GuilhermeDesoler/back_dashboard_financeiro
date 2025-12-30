"""
Script de inicialização da empresa administrativa

Cria:
- Empresa administrativa (não aparece na listagem normal)
- Super admin vinculado à empresa administrativa
- Database isolado para a empresa administrativa
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.database import MongoConnection, get_shared_db
from src.infra.repositories import MongoCompanyRepository, MongoUserRepository, MongoFeatureRepository, MongoRoleRepository
from src.domain.entities import Company, User, Role
from src.infra.security import PasswordHash
from src.infra.database.tenant_database_manager import TenantDatabaseManager


def init_admin_company():
    """Inicializa a empresa administrativa e o super admin"""
    print("🔧 Inicializando empresa administrativa...")

    # Conectar ao MongoDB
    MongoConnection()
    shared_db = get_shared_db()

    # Repositórios
    company_repo = MongoCompanyRepository(shared_db["companies"])
    user_repo = MongoUserRepository(shared_db["users"])
    feature_repo = MongoFeatureRepository(shared_db["features"])

    # ========== EMPRESA ADMINISTRATIVA ==========

    # Verificar se já existe
    admin_company = company_repo.find_by_cnpj("00.000.000/0000-00")

    if admin_company:
        print(f"⏭️  Empresa administrativa já existe: {admin_company.name}")
    else:
        admin_company = Company(
            name="Administração do Sistema",
            cnpj="00.000.000/0000-00",
            phone="(00) 00000-0000",
            plan="system",
            is_active=True,
            is_admin_company=True,  # Marca como empresa administrativa
            settings={"timezone": "America/Sao_Paulo", "currency": "BRL"}
        )

        admin_company = company_repo.create(admin_company)

        # Criar database da empresa administrativa
        tenant_manager = TenantDatabaseManager()
        tenant_db = tenant_manager.create_tenant_db(admin_company.id)

        print(f"✅ Empresa administrativa criada: {admin_company.name}")
        print(f"   Database: {tenant_db.name}")

    # ========== ROLE SUPER ADMIN ==========

    from src.database import get_tenant_db
    tenant_db = get_tenant_db(admin_company.id)
    role_repo = MongoRoleRepository(tenant_db["roles"])

    # Buscar todas as features
    all_features = feature_repo.find_all()
    all_feature_ids = [f.id for f in all_features]

    # Verificar se role Super Admin já existe
    existing_roles = role_repo.find_all()
    super_admin_role = None
    for role in existing_roles:
        if role.name == "Super Admin":
            super_admin_role = role
            break

    if not super_admin_role:
        super_admin_role = Role(
            name="Super Admin",
            company_id=admin_company.id,
            description="Super administrador do sistema",
            feature_ids=all_feature_ids
        )
        super_admin_role = role_repo.create(super_admin_role)
        print(f"✅ Role Super Admin criada")
    else:
        print(f"⏭️  Role Super Admin já existe")

    # ========== SUPER ADMIN USER ==========

    # Verificar se super admin já existe
    super_admin_user = user_repo.find_by_email("admin@sistema.com")

    if super_admin_user:
        print(f"⏭️  Super admin já existe: {super_admin_user.email}")
    else:
        super_admin_user = User(
            email="admin@sistema.com",
            password_hash=PasswordHash.hash("admin123"),
            name="Super Administrador",
            company_id=admin_company.id,
            role_ids=[super_admin_role.id],
            is_active=True,
            is_super_admin=True
        )

        super_admin_user = user_repo.create(super_admin_user)
        print(f"✅ Super admin criado: {super_admin_user.email}")

    # ========== RESUMO ==========

    print("\n" + "="*60)
    print("🎉 INICIALIZAÇÃO CONCLUÍDA!")
    print("="*60)

    print(f"\n📊 Resumo:")
    print(f"  • Empresa administrativa: {admin_company.name}")
    print(f"  • CNPJ: {admin_company.cnpj}")
    print(f"  • is_admin_company: {admin_company.is_admin_company}")
    print(f"  • Super admin criado: {super_admin_user.email}")

    print(f"\n🔑 Credenciais do Super Admin:")
    print(f"  Email: admin@sistema.com")
    print(f"  Senha: admin123")

    print(f"\n⚠️  IMPORTANTE:")
    print(f"  • Esta empresa NÃO aparece na listagem de empresas")
    print(f"  • Super admin está vinculado à empresa administrativa")
    print(f"  • Super admin tem acesso a todas as funcionalidades")
    print(f"  • Super admin pode fazer impersonate de qualquer empresa")

    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        init_admin_company()
    except Exception as e:
        print(f"\n❌ Erro durante a inicialização: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
