"""
Script para resetar TUDO e popular com dados de teste limpos

ATENÇÃO: Este script DELETA TODOS os dados e recria do zero

Usuários de teste:
1. super@teste.com / 123456 - Super Admin (não vinculado a empresa)
2. admin@teste.com / 123456 - Admin (vinculado a empresa)
3. usuario@teste.com / 123456 - Usuário comum (sem role)

Execute:
  python scripts/reset_and_seed.py --yes  # Auto-confirma a deleção
  python scripts/reset_and_seed.py        # Pede confirmação
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.mongo_connection import MongoConnection, get_shared_db, create_tenant_db
from src.domain.entities import Feature, Company, User, Role
from src.infra.repositories import (
    MongoFeatureRepository,
    MongoCompanyRepository,
    MongoUserRepository,
    MongoRoleRepository
)
from src.infra.security import PasswordHash


def drop_all_databases(auto_confirm=False):
    """Deleta TODOS os bancos de dados (exceto admin, config, local)"""
    print("🗑️  DELETANDO TODOS OS BANCOS DE DADOS...")

    mongo = MongoConnection()
    client = mongo.client

    # Lista todos os databases
    db_list = client.list_database_names()

    # Filtra databases do sistema que não devem ser deletados
    system_dbs = ['admin', 'config', 'local']
    user_dbs = [db for db in db_list if db not in system_dbs]

    if not user_dbs:
        print("   ℹ️  Nenhum banco de dados para deletar")
        return

    print(f"   Encontrados {len(user_dbs)} bancos de dados:")
    for db_name in user_dbs:
        print(f"      - {db_name}")

    if not auto_confirm:
        confirm = input("\n   ⚠️  TEM CERTEZA que deseja DELETAR TUDO? (digite 'SIM' para confirmar): ")
        if confirm != "SIM":
            print("   ❌ Operação cancelada pelo usuário")
            sys.exit(0)
    else:
        print("\n   ⚠️  Auto-confirmação ativada, deletando todos os bancos...")

    for db_name in user_dbs:
        client.drop_database(db_name)
        print(f"   ✅ Deletado: {db_name}")

    print(f"\n   🗑️  {len(user_dbs)} bancos de dados deletados!\n")


def seed_features(feature_repo):
    """Cria todas as features do sistema"""
    print("📦 Criando Features do Sistema...")

    features = [
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

        # Installments
        Feature(
            code="installments.create",
            name="Criar Parcelas",
            description="Permite criar parcelas de pagamento",
            module="installments",
            is_system=True
        ),
        Feature(
            code="installments.read",
            name="Visualizar Parcelas",
            description="Permite visualizar parcelas",
            module="installments",
            is_system=True
        ),
        Feature(
            code="installments.update",
            name="Atualizar Parcelas",
            description="Permite atualizar parcelas",
            module="installments",
            is_system=True
        ),
        Feature(
            code="installments.delete",
            name="Deletar Parcelas",
            description="Permite deletar parcelas",
            module="installments",
            is_system=True
        ),

        # Bank Limits
        Feature(
            code="bank_limits.create",
            name="Criar Limites Bancários",
            description="Permite criar limites bancários",
            module="bank_limits",
            is_system=True
        ),
        Feature(
            code="bank_limits.read",
            name="Visualizar Limites Bancários",
            description="Permite visualizar limites bancários",
            module="bank_limits",
            is_system=True
        ),
        Feature(
            code="bank_limits.update",
            name="Atualizar Limites Bancários",
            description="Permite atualizar limites bancários",
            module="bank_limits",
            is_system=True
        ),
        Feature(
            code="bank_limits.delete",
            name="Deletar Limites Bancários",
            description="Permite deletar limites bancários",
            module="bank_limits",
            is_system=True
        ),

        # Platform Settings
        Feature(
            code="platform_settings.read",
            name="Visualizar Configurações da Plataforma",
            description="Permite visualizar configurações da plataforma",
            module="platform_settings",
            is_system=True
        ),
        Feature(
            code="platform_settings.update",
            name="Atualizar Configurações da Plataforma",
            description="Permite atualizar configurações da plataforma",
            module="platform_settings",
            is_system=True
        ),

        # Users
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

        # Roles
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

    for feature in features:
        feature_repo.create(feature)

    print(f"   ✅ {len(features)} features criadas\n")

    return features


def seed_modalities(tenant_db):
    """Cria modalidades de pagamento baseadas na tabela fornecida"""
    print("💳 Criando Modalidades de Pagamento...")

    from src.infra.repositories import MongoPaymentModalityRepository
    from src.domain.entities import PaymentModality

    modality_repo = MongoPaymentModalityRepository(tenant_db["payment_modalities"])

    # Modalidades baseadas na tabela fornecida
    modalities_data = [
        # Sicredi
        {"name": "PIX Sicredi", "bank": "Sicredi", "fee": 0.0, "rental": 0.0, "color": "#32CCBC"},
        {"name": "Débito Sicredi", "bank": "Sicredi", "fee": 0.9, "rental": 0.0, "color": "#FF6B6B"},
        {"name": "Crédito à Vista Sicredi", "bank": "Sicredi", "fee": 1.1, "rental": 0.0, "color": "#4ECDC4"},
        {"name": "Crédito 2 a 6 Sicredi", "bank": "Sicredi", "fee": 1.4, "rental": 0.0, "color": "#45B7D1"},
        {"name": "Crédito 7 a 12 Sicredi", "bank": "Sicredi", "fee": 1.6, "rental": 0.0, "color": "#96CEB4"},
        {"name": "Antecipação Sicredi", "bank": "Sicredi", "fee": 1.7, "rental": 0.0, "color": "#FFEAA7", "allows_anticipation": True},
        {"name": "Máquinas Sicredi", "bank": "Sicredi", "fee": 2.0, "rental": 0.0, "color": "#DFE6E9"},
        {"name": "Aluguel Sicredi", "bank": "Sicredi", "fee": 0.0, "rental": 0.0, "color": "#74B9FF"},
        
        # Sicoob
        {"name": "PIX Sicoob", "bank": "Sicoob", "fee": 0.0, "rental": 0.0, "color": "#32CCBC"},
        {"name": "Débito Sicoob", "bank": "Sicoob", "fee": 0.9, "rental": 0.0, "color": "#FF6B6B"},
        {"name": "Crédito à Vista Sicoob", "bank": "Sicoob", "fee": 1.1, "rental": 0.0, "color": "#4ECDC4"},
        {"name": "Crédito 2 a 6 Sicoob", "bank": "Sicoob", "fee": 1.4, "rental": 0.0, "color": "#45B7D1"},
        {"name": "Crédito 7 a 12 Sicoob", "bank": "Sicoob", "fee": 1.6, "rental": 0.0, "color": "#96CEB4"},
        {"name": "Antecipação Sicoob", "bank": "Sicoob", "fee": 1.59, "rental": 0.0, "color": "#FFEAA7", "allows_anticipation": True},
        {"name": "Máquinas Sicoob", "bank": "Sicoob", "fee": 1.0, "rental": 0.0, "color": "#DFE6E9"},
        {"name": "Aluguel Sicoob", "bank": "Sicoob", "fee": 0.0, "rental": 56.90, "color": "#74B9FF"},
        
        # Link Sicredi
        {"name": "PIX Link Sicredi", "bank": "Link Sicredi", "fee": 0.0, "rental": 0.0, "color": "#32CCBC"},
        {"name": "Débito Link Sicredi", "bank": "Link Sicredi", "fee": 0.9, "rental": 0.0, "color": "#FF6B6B"},
        {"name": "Crédito à Vista Link Sicredi", "bank": "Link Sicredi", "fee": 1.3, "rental": 0.0, "color": "#4ECDC4"},
        {"name": "Crédito 2 a 6 Link Sicredi", "bank": "Link Sicredi", "fee": 1.6, "rental": 0.0, "color": "#45B7D1"},
        {"name": "Crédito 7 a 12 Link Sicredi", "bank": "Link Sicredi", "fee": 1.8, "rental": 0.0, "color": "#96CEB4"},
        {"name": "Antecipação Link Sicredi", "bank": "Link Sicredi", "fee": 1.79, "rental": 0.0, "color": "#FFEAA7", "allows_anticipation": True},
    ]

    created_count = 0
    for mod_data in modalities_data:
        modality = PaymentModality(
            name=mod_data["name"],
            bank_name=mod_data["bank"],
            color=mod_data["color"],
            fee_percentage=mod_data["fee"],
            rental_fee=mod_data.get("rental", 0.0),
            is_active=True,
            allows_anticipation=mod_data.get("allows_anticipation", False),
        )
        modality_repo.create(modality)
        created_count += 1

    print(f"   ✅ {created_count} modalidades criadas\n")



def seed_all(auto_confirm=False):
    """Popula todo o banco de dados com dados de teste"""

    print("=" * 80)
    print("🌱 RESET E SEED COMPLETO DO SISTEMA")
    print("=" * 80)
    print()

    # Deleta tudo
    drop_all_databases(auto_confirm)

    # Agora recria tudo do zero
    shared_db = get_shared_db()

    print("=" * 80)
    print("🌱 CRIANDO DADOS DE TESTE")
    print("=" * 80)
    print()

    # ========== 1. FEATURES ==========
    feature_repo = MongoFeatureRepository(shared_db["features"])
    features = seed_features(feature_repo)
    feature_ids = [f.id for f in features if f.is_system]

    # ========== 2. EMPRESA DE TESTE ==========
    print("🏢 Criando Empresa de Teste...")

    company_repo = MongoCompanyRepository(shared_db["companies"])

    test_company = Company(
        name="Empresa Teste Ltda",
        cnpj="11.222.333/0001-44",
        phone="(11) 98765-4321",
        plan="premium"
    )
    test_company = company_repo.create(test_company)

    # Cria o banco de dados da empresa com nome legível
    tenant_db = create_tenant_db(test_company.id, test_company.name)

    print(f"   ✅ Empresa criada: {test_company.name}")
    print(f"   📋 ID: {test_company.id}")
    print(f"   📞 Telefone: {test_company.phone}")
    print(f"   💾 Database: {tenant_db.name}\n")

    # ========== 3. ROLE ADMIN ==========
    print("👑 Criando Role Admin...")

    role_repo = MongoRoleRepository(tenant_db["roles"])

    admin_role = Role(
        name="Admin",
        company_id=test_company.id,
        feature_ids=feature_ids
    )
    admin_role = role_repo.create(admin_role)
    print(f"   ✅ Role Admin criada com {len(feature_ids)} features\n")

    # ========== 3.5. ROLE USUÁRIO ==========
    print("👤 Criando Role Usuário...")
    
    # Features excluindo as de admin (roles, users, company)
    user_feature_ids = [
        f.id for f in features 
        if f.is_system and not any(x in f.code for x in ['roles.', 'users.', 'company.'])
    ]
    
    user_role = Role(
        name="Usuário",
        company_id=test_company.id,
        feature_ids=user_feature_ids
    )
    user_role = role_repo.create(user_role)
    print(f"   ✅ Role Usuário criada com {len(user_feature_ids)} features\n")

    # ========== 3.6. MODALIDADES DE PAGAMENTO ==========
    seed_modalities(tenant_db)

    # ========== 4. USUÁRIOS DE TESTE ==========
    print("👥 Criando Usuários de Teste...")

    user_repo = MongoUserRepository(shared_db["users"])

    # 1. Super Admin (não vinculado a empresa)
    super_user = User(
        email="super@teste.com",
        password_hash=PasswordHash.hash("123456"),
        name="Super Admin",
        company_id=None,  # NÃO vinculado a empresa
        role_ids=[],  # Sem roles específicas
        is_active=True,
        is_super_admin=True
    )
    super_user = user_repo.create(super_user)

    print(f"   ✅ Super Admin criado:")
    print(f"      📧 Email: {super_user.email}")
    print(f"      🔑 Senha: 123456")
    print(f"      👤 Nome: {super_user.name}")
    print(f"      🏢 Empresa: Nenhuma (super admin global)")
    print(f"      ⭐ Super Admin: SIM\n")

    # 2. Admin (vinculado a empresa com role)
    admin_user = User(
        email="admin@teste.com",
        password_hash=PasswordHash.hash("123456"),
        name="Admin da Empresa",
        company_id=test_company.id,
        role_ids=[admin_role.id],
        is_active=True,
        is_super_admin=False
    )
    admin_user = user_repo.create(admin_user)

    print(f"   ✅ Admin criado:")
    print(f"      📧 Email: {admin_user.email}")
    print(f"      🔑 Senha: 123456")
    print(f"      👤 Nome: {admin_user.name}")
    print(f"      🏢 Empresa: {test_company.name}")
    print(f"      👑 Role: Admin")
    print(f"      ⭐ Super Admin: NÃO\n")

    # 3. Usuário comum (vinculado a empresa, com role de usuário)
    common_user = User(
        email="usuario@teste.com",
        password_hash=PasswordHash.hash("123456"),
        name="Usuário Comum",
        company_id=test_company.id,
        role_ids=[user_role.id],  # Role de Usuário
        is_active=True,
        is_super_admin=False
    )
    common_user = user_repo.create(common_user)

    print(f"   ✅ Usuário Comum criado:")
    print(f"      📧 Email: {common_user.email}")
    print(f"      🔑 Senha: 123456")
    print(f"      👤 Nome: {common_user.name}")
    print(f"      🏢 Empresa: {test_company.name}")
    print(f"      👑 Role: Usuário")
    print(f"      ⭐ Super Admin: NÃO\n")

    # ========== RESUMO FINAL ==========
    print("=" * 80)
    print("🎉 RESET E SEED COMPLETO CONCLUÍDO!")
    print("=" * 80)
    print(f"\n📊 Resumo:")
    print(f"   • Features: {len(features)}")
    print(f"   • Empresa: {test_company.name} ({test_company.cnpj})")
    print(f"   • Database: {tenant_db.name}")
    print(f"   • Modalidades: 22 (Sicredi, Sicoob, Link Sicredi)")
    print(f"   • Roles:")
    print(f"      - Admin: {len(feature_ids)} features (acesso total)")
    print(f"      - Usuário: {len(user_feature_ids)} features (sem acesso a roles, users, company)")
    print(f"   • Usuários: 3")
    print(f"\n👥 Credenciais de Teste:")
    print(f"\n   1️⃣  SUPER ADMIN (acesso global)")
    print(f"      Email: super@teste.com")
    print(f"      Senha: 123456")
    print(f"\n   2️⃣  ADMIN (acesso total à empresa)")
    print(f"      Email: admin@teste.com")
    print(f"      Senha: 123456")
    print(f"\n   3️⃣  USUÁRIO COMUM (acesso limitado)")
    print(f"      Email: usuario@teste.com")
    print(f"      Senha: 123456")
    print(f"\n🚀 Para testar:")
    print(f"   1. python src/app.py")
    print(f"   2. POST http://localhost:5000/api/auth/login")
    print(f"      {{")
    print(f"        \"email\": \"admin@teste.com\",")
    print(f"        \"password\": \"123456\"")
    print(f"      }}")
    print(f"\n✨ Pronto para uso!\n")


if __name__ == "__main__":
    # Verifica se foi passado --yes como argumento
    auto_confirm = "--yes" in sys.argv or "-y" in sys.argv
    seed_all(auto_confirm)
