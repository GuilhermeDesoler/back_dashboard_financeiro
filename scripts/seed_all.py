"""
Script para popular TUDO no sistema:
- Features
- Empresa de teste
- Role Admin para a empresa
- Usuário teste

Execute: python scripts/seed_all.py
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_shared_db, get_tenant_db, create_tenant_db
from src.domain.entities import Feature, Company, User, Role
from src.infra.repositories import (
    MongoFeatureRepository,
    MongoCompanyRepository,
    MongoUserRepository,
    MongoRoleRepository
)
from src.infra.security import PasswordHash


def seed_all():
    """Popula todo o banco de dados com dados de teste"""

    shared_db = get_shared_db()

    print("🌱 Iniciando seed completo do sistema...\n")

    # ========== 1. FEATURES ==========
    print("📦 1/4 - Criando Features do Sistema...")

    feature_repo = MongoFeatureRepository(shared_db["features"])

    system_features = [
        # Financial Entries
        Feature(
            code="financial_entries.create",
            name="Criar Lançamentos Financeiros",
            description="Permite criar novos lançamentos financeiros",
            module="financial_entries",
            is_system=True
        ),
        Feature(
            code="financial_entries.read",
            name="Visualizar Lançamentos Financeiros",
            description="Permite visualizar lançamentos financeiros",
            module="financial_entries",
            is_system=True
        ),
        Feature(
            code="financial_entries.update",
            name="Atualizar Lançamentos Financeiros",
            description="Permite atualizar lançamentos financeiros existentes",
            module="financial_entries",
            is_system=True
        ),
        Feature(
            code="financial_entries.delete",
            name="Deletar Lançamentos Financeiros",
            description="Permite deletar lançamentos financeiros",
            module="financial_entries",
            is_system=True
        ),

        # Payment Modalities
        Feature(
            code="payment_modalities.create",
            name="Criar Modalidades de Pagamento",
            description="Permite criar novas modalidades de pagamento",
            module="payment_modalities",
            is_system=True
        ),
        Feature(
            code="payment_modalities.read",
            name="Visualizar Modalidades de Pagamento",
            description="Permite visualizar modalidades de pagamento",
            module="payment_modalities",
            is_system=True
        ),
        Feature(
            code="payment_modalities.update",
            name="Atualizar Modalidades de Pagamento",
            description="Permite atualizar modalidades de pagamento",
            module="payment_modalities",
            is_system=True
        ),
        Feature(
            code="payment_modalities.delete",
            name="Deletar Modalidades de Pagamento",
            description="Permite deletar modalidades de pagamento",
            module="payment_modalities",
            is_system=True
        ),
        Feature(
            code="payment_modalities.toggle",
            name="Ativar/Desativar Modalidades",
            description="Permite ativar ou desativar modalidades de pagamento",
            module="payment_modalities",
            is_system=True
        ),

        # Users (Admin only)
        Feature(
            code="users.create",
            name="Criar Usuários",
            description="Permite criar novos usuários na empresa",
            module="users",
            is_system=True
        ),
        Feature(
            code="users.read",
            name="Visualizar Usuários",
            description="Permite visualizar usuários da empresa",
            module="users",
            is_system=True
        ),
        Feature(
            code="users.update",
            name="Atualizar Usuários",
            description="Permite atualizar dados de usuários",
            module="users",
            is_system=True
        ),
        Feature(
            code="users.delete",
            name="Deletar Usuários",
            description="Permite deletar usuários",
            module="users",
            is_system=True
        ),

        # Roles (Admin only)
        Feature(
            code="roles.create",
            name="Criar Roles",
            description="Permite criar novas roles/papéis",
            module="roles",
            is_system=True
        ),
        Feature(
            code="roles.read",
            name="Visualizar Roles",
            description="Permite visualizar roles/papéis",
            module="roles",
            is_system=True
        ),
        Feature(
            code="roles.update",
            name="Atualizar Roles",
            description="Permite atualizar roles/papéis",
            module="roles",
            is_system=True
        ),
        Feature(
            code="roles.delete",
            name="Deletar Roles",
            description="Permite deletar roles/papéis",
            module="roles",
            is_system=True
        ),

        # Company
        Feature(
            code="company.create",
            name="Criar Empresas",
            description="Permite criar novas empresas (super admin)",
            module="company",
            is_system=True
        ),
        Feature(
            code="company.read",
            name="Visualizar Empresas",
            description="Permite visualizar empresas",
            module="company",
            is_system=True
        ),
        Feature(
            code="company.settings.read",
            name="Visualizar Configurações da Empresa",
            description="Permite visualizar configurações da empresa",
            module="company",
            is_system=True
        ),
        Feature(
            code="company.settings.update",
            name="Atualizar Configurações da Empresa",
            description="Permite atualizar configurações da empresa",
            module="company",
            is_system=True
        ),

        # Reports
        Feature(
            code="reports.financial_summary",
            name="Relatório Resumo Financeiro",
            description="Permite visualizar relatório de resumo financeiro",
            module="reports",
            is_system=True
        ),
        Feature(
            code="reports.export",
            name="Exportar Relatórios",
            description="Permite exportar relatórios em diversos formatos",
            module="reports",
            is_system=True
        ),
    ]

    created_features = 0
    existing_features = 0

    for feature in system_features:
        existing = feature_repo.find_by_code(feature.code)
        if existing:
            existing_features += 1
        else:
            feature_repo.create(feature)
            created_features += 1

    print(f"   ✅ Criadas: {created_features}")
    print(f"   ⏭️  Já existiam: {existing_features}")
    print(f"   📦 Total: {len(system_features)}\n")

    # ========== 2. EMPRESA DE TESTE ==========
    print("🏢 2/4 - Criando Empresa de Teste...")

    company_repo = MongoCompanyRepository(shared_db["companies"])

    test_company_cnpj = "11.222.333/0001-44"
    existing_company = company_repo.find_by_cnpj(test_company_cnpj)

    if existing_company:
        print(f"   ⏭️  Empresa de teste já existe: {existing_company.name}")
        test_company = existing_company
    else:
        test_company = Company(
            name="Empresa Teste Ltda",
            cnpj=test_company_cnpj,
            phone="(11) 98765-4321",
            plan="premium"
        )
        test_company = company_repo.create(test_company)

        # Cria o banco de dados da empresa
        create_tenant_db(test_company.id)

        print(f"   ✅ Empresa criada: {test_company.name}")
        print(f"   📋 ID: {test_company.id}")
        print(f"   📞 Telefone: {test_company.phone}\n")

    # ========== 3. ROLE ADMIN ==========
    print("👑 3/4 - Criando Role Admin para a Empresa...")

    tenant_db = get_tenant_db(test_company.id)
    role_repo = MongoRoleRepository(tenant_db["roles"])

    # Busca todas as features para atribuir ao admin
    all_features = feature_repo.find_all()
    feature_ids = [f.id for f in all_features if f.is_system]

    existing_admin_role = role_repo.find_by_name("Admin", test_company.id)

    if existing_admin_role:
        print(f"   ⏭️  Role Admin já existe")
        admin_role = existing_admin_role
    else:
        admin_role = Role(
            name="Admin",
            company_id=test_company.id,
            feature_ids=feature_ids
        )
        admin_role = role_repo.create(admin_role)
        print(f"   ✅ Role Admin criada com {len(feature_ids)} features\n")

    # ========== 4. USUÁRIO TESTE ==========
    print("👤 4/4 - Criando Usuário Teste...")

    user_repo = MongoUserRepository(shared_db["users"])

    test_email = "teste@teste.com"
    existing_user = user_repo.find_by_email(test_email)

    if existing_user:
        print(f"   ⏭️  Usuário teste já existe: {test_email}")
        test_user = existing_user
    else:
        password_hash = PasswordHash.hash("123456")

        test_user = User(
            email=test_email,
            password_hash=password_hash,
            name="Usuário Teste",
            company_id=test_company.id,
            role_ids=[admin_role.id],
            is_active=True,
            is_super_admin=True  # Super Admin - pode acessar todas as empresas
        )
        test_user = user_repo.create(test_user)

        print(f"   ✅ Usuário criado: {test_user.email}")
        print(f"   🔑 Senha: 123456")
        print(f"   👤 Nome: {test_user.name}")
        print(f"   🏢 Empresa: {test_company.name}")
        print(f"   👑 Role: Admin")
        print(f"   ⭐ Super Admin: SIM\n")

    # ========== RESUMO FINAL ==========
    print("=" * 60)
    print("🎉 SEED COMPLETO CONCLUÍDO!")
    print("=" * 60)
    print(f"\n📊 Resumo:")
    print(f"   • Features: {len(system_features)} (criadas: {created_features}, existentes: {existing_features})")
    print(f"   • Empresa: {test_company.name} ({test_company.cnpj})")
    print(f"   • Banco da empresa: company_{test_company.id}_db")
    print(f"   • Role: Admin com {len(feature_ids)} features")
    print(f"   • Usuário: {test_email} (senha: 123456)")
    print(f"\n🚀 Para testar:")
    print(f"   1. python src/app.py")
    print(f"   2. POST http://localhost:5000/api/auth/login")
    print(f"      {{")
    print(f"        \"email\": \"teste@teste.com\",")
    print(f"        \"password\": \"123456\"")
    print(f"      }}")
    print(f"\n✨ Pronto para uso!\n")


if __name__ == "__main__":
    seed_all()
