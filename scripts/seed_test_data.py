"""
Script de seed para dados de teste

Cria:
- 3 empresas (além da já existente)
- Múltiplos usuários por empresa
- Modalidades de pagamento
- Lançamentos financeiros
"""

import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from datetime import datetime, timedelta
from src.database import MongoConnection, get_shared_db, get_tenant_db
from src.infra.repositories import (
    MongoCompanyRepository,
    MongoUserRepository,
    MongoFeatureRepository,
    MongoRoleRepository,
    MongoPaymentModalityRepository,
    MongoFinancialEntryRepository
)
from src.domain.entities import Company, User, Role, PaymentModality, FinancialEntry
from src.infra.security import PasswordHash
from src.infra.database.tenant_database_manager import TenantDatabaseManager
import random


def seed_test_data():
    """Seed completo de dados de teste"""
    print("🌱 Iniciando seed de dados de teste...")

    # Conectar ao MongoDB
    MongoConnection()
    shared_db = get_shared_db()

    # Repositórios
    company_repo = MongoCompanyRepository(shared_db["companies"])
    user_repo = MongoUserRepository(shared_db["users"])
    feature_repo = MongoFeatureRepository(shared_db["features"])

    # Buscar todas as features para criar roles
    all_features = feature_repo.find_all()
    all_feature_ids = [f.id for f in all_features]

    print(f"✅ {len(all_features)} features disponíveis")

    # ========== EMPRESAS ==========

    companies_data = [
        {
            "name": "Tech Solutions Ltda",
            "cnpj": "11.222.333/0001-44",
            "phone": "(11) 98765-4321",
            "plan": "premium"
        },
        {
            "name": "Comercial ABC S.A.",
            "cnpj": "22.333.444/0001-55",
            "phone": "(21) 91234-5678",
            "plan": "basic"
        },
        {
            "name": "Indústria XYZ Eireli",
            "cnpj": "33.444.555/0001-66",
            "phone": "(47) 99999-8888",
            "plan": "enterprise"
        }
    ]

    created_companies = []

    for comp_data in companies_data:
        # Verificar se já existe
        existing = company_repo.find_by_cnpj(comp_data["cnpj"])
        if existing:
            print(f"⏭️  Empresa {comp_data['name']} já existe")
            created_companies.append(existing)
            continue

        company = Company(
            name=comp_data["name"],
            cnpj=comp_data["cnpj"],
            phone=comp_data["phone"],
            plan=comp_data["plan"],
            is_active=True,
            settings={"timezone": "America/Sao_Paulo", "currency": "BRL"}
        )

        created_company = company_repo.create(company)
        created_companies.append(created_company)

        # Criar database da empresa
        tenant_manager = TenantDatabaseManager()
        tenant_db = tenant_manager.create_tenant_db(created_company.id)

        print(f"✅ Empresa criada: {comp_data['name']} (DB: {tenant_db.name})")

    # ========== USUÁRIOS E DADOS POR EMPRESA ==========

    for idx, company in enumerate(created_companies):
        print(f"\n📊 Criando dados para: {company.name}")

        # Database da empresa
        tenant_db = get_tenant_db(company.id)
        role_repo = MongoRoleRepository(tenant_db["roles"])
        modality_repo = MongoPaymentModalityRepository(tenant_db["payment_modalities"])
        entry_repo = MongoFinancialEntryRepository(tenant_db["financial_entries"])

        # ========== ROLE ADMIN ==========

        # Verificar se role Admin já existe
        existing_roles = role_repo.find_all()
        admin_role = None
        for role in existing_roles:
            if role.name == "Admin":
                admin_role = role
                break

        if not admin_role:
            admin_role = Role(
                name="Admin",
                company_id=company.id,
                description="Administrador da empresa",
                feature_ids=all_feature_ids
            )
            admin_role = role_repo.create(admin_role)
            print(f"  ✅ Role Admin criada")
        else:
            print(f"  ⏭️  Role Admin já existe")

        # ========== USUÁRIOS ==========

        users_data = [
            {
                "email": f"admin@empresa{idx+1}.com",
                "password": "senha123",
                "name": f"Administrador da {company.name.split()[0]}",
                "roles": [admin_role.id]
            },
            {
                "email": f"financeiro@empresa{idx+1}.com",
                "password": "senha123",
                "name": f"Gerente Financeiro - {company.name.split()[0]}",
                "roles": [admin_role.id]
            },
            {
                "email": f"operador@empresa{idx+1}.com",
                "password": "senha123",
                "name": f"Operador - {company.name.split()[0]}",
                "roles": [admin_role.id]
            }
        ]

        created_users = []

        for user_data in users_data:
            # Verificar se usuário já existe
            existing_user = user_repo.find_by_email(user_data["email"])
            if existing_user:
                print(f"  ⏭️  Usuário {user_data['email']} já existe")
                created_users.append(existing_user)
                continue

            user = User(
                email=user_data["email"],
                password_hash=PasswordHash.hash(user_data["password"]),
                name=user_data["name"],
                company_id=company.id,
                role_ids=user_data["roles"],
                is_active=True,
                is_super_admin=False
            )

            created_user = user_repo.create(user)
            created_users.append(created_user)
            print(f"  ✅ Usuário criado: {user_data['email']}")

        # ========== MODALIDADES DE PAGAMENTO ==========

        modalities_data = [
            {"name": "PIX", "color": "#00FF00"},
            {"name": "Dinheiro", "color": "#FFD700"},
            {"name": "Cartão de Crédito", "color": "#0000FF"},
            {"name": "Cartão de Débito", "color": "#FF6347"},
            {"name": "Boleto", "color": "#FF0000"},
            {"name": "Transferência Bancária", "color": "#4B0082"}
        ]

        created_modalities = []

        for mod_data in modalities_data:
            modality = PaymentModality(
                name=mod_data["name"],
                color=mod_data["color"],
                is_active=True
            )

            try:
                created_modality = modality_repo.create(modality)
                created_modalities.append(created_modality)
            except:
                # Pode já existir, ignorar
                pass

        print(f"  ✅ {len(created_modalities)} modalidades de pagamento criadas")

        # ========== LANÇAMENTOS FINANCEIROS ==========

        # Criar lançamentos dos últimos 60 dias
        entries_created = 0
        start_date = datetime.now() - timedelta(days=60)

        for day in range(60):
            current_date = start_date + timedelta(days=day)

            # 1-5 lançamentos por dia
            num_entries = random.randint(1, 5)

            for _ in range(num_entries):
                if not created_modalities:
                    break

                modality = random.choice(created_modalities)

                # Valor aleatório entre 50.00 e 5000.00
                value = round(random.uniform(50.0, 5000.0), 2)

                entry = FinancialEntry(
                    value=value,
                    date=current_date,
                    modality_id=modality.id,
                    modality_name=modality.name,
                    modality_color=modality.color
                )

                try:
                    entry_repo.create(entry)
                    entries_created += 1
                except:
                    pass

        print(f"  ✅ {entries_created} lançamentos financeiros criados")

    # ========== EMPRESA DE TESTE (já existente) ==========

    print(f"\n📊 Adicionando dados para: Empresa Teste Ltda (se existir)")

    test_company = company_repo.find_by_cnpj("00.000.000/0001-00")

    if test_company:
        tenant_db = get_tenant_db(test_company.id)
        modality_repo = MongoPaymentModalityRepository(tenant_db["payment_modalities"])
        entry_repo = MongoFinancialEntryRepository(tenant_db["financial_entries"])

        # Modalidades (se não existirem)
        for mod_data in modalities_data:
            modality = PaymentModality(
                name=mod_data["name"],
                color=mod_data["color"],
                is_active=True
            )

            try:
                modality_repo.create(modality)
            except:
                pass

        # Buscar modalidades criadas
        modalities = modality_repo.find_all()

        # Lançamentos
        entries_created = 0
        start_date = datetime.now() - timedelta(days=60)

        for day in range(60):
            current_date = start_date + timedelta(days=day)
            num_entries = random.randint(1, 5)

            for _ in range(num_entries):
                if not modalities:
                    break

                modality = random.choice(modalities)
                value = round(random.uniform(50.0, 5000.0), 2)

                entry = FinancialEntry(
                    value=value,
                    date=current_date,
                    modality_id=modality.id,
                    modality_name=modality.name,
                    modality_color=modality.color
                )

                try:
                    entry_repo.create(entry)
                    entries_created += 1
                except:
                    pass

        print(f"  ✅ {entries_created} lançamentos financeiros criados")

    # ========== RESUMO ==========

    print("\n" + "="*60)
    print("🎉 SEED CONCLUÍDO COM SUCESSO!")
    print("="*60)

    print(f"\n📊 Resumo:")
    print(f"  • {len(created_companies)} empresas criadas/atualizadas")
    print(f"  • ~{len(created_companies) * 3} usuários criados")
    print(f"  • {len(modalities_data)} modalidades por empresa")
    print(f"  • ~{60 * 3} lançamentos por empresa (últimos 60 dias)")

    print(f"\n🔑 Credenciais de Teste:")
    print(f"\n  Super Admin:")
    print(f"    Email: teste@teste.com")
    print(f"    Senha: 123456")

    for idx, company in enumerate(created_companies):
        print(f"\n  {company.name}:")
        print(f"    Admin:      admin@empresa{idx+1}.com / senha123")
        print(f"    Financeiro: financeiro@empresa{idx+1}.com / senha123")
        print(f"    Operador:   operador@empresa{idx+1}.com / senha123")

    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        seed_test_data()
    except Exception as e:
        print(f"\n❌ Erro durante o seed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
