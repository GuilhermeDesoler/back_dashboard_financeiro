"""
Script para criar roles padrão para uma empresa

Execute: python scripts/seed_roles.py <company_id>
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_shared_db, get_tenant_db
from src.domain.entities import Role, Feature
from src.infra.repositories import MongoRoleRepository, MongoFeatureRepository


def seed_roles(company_id: str):
    """Cria roles padrão para uma empresa específica"""

    shared_db = get_shared_db()
    tenant_db = get_tenant_db(company_id)

    role_repo = MongoRoleRepository(tenant_db["roles"])
    feature_repo = MongoFeatureRepository(shared_db["features"])

    # Busca todas as features do sistema
    all_features = feature_repo.find_all()
    feature_dict = {f.code: f.id for f in all_features}

    # Define roles padrão
    default_roles = [
        {
            "name": "Admin",
            "description": "Administrador com acesso total ao sistema",
            "features": [
                # Financial Entries - todas
                "financial_entries.create",
                "financial_entries.read",
                "financial_entries.update",
                "financial_entries.delete",

                # Payment Modalities - todas
                "payment_modalities.create",
                "payment_modalities.read",
                "payment_modalities.update",
                "payment_modalities.delete",
                "payment_modalities.toggle",

                # Users - todas (admin only)
                "users.create",
                "users.read",
                "users.update",
                "users.delete",

                # Roles - todas (admin only)
                "roles.create",
                "roles.read",
                "roles.update",
                "roles.delete",

                # Company Settings - todas (admin only)
                "company.settings.read",
                "company.settings.update",

                # Reports - todas
                "reports.financial_summary",
                "reports.export",
            ]
        },
        {
            "name": "Gerente",
            "description": "Gerente com acesso a operações financeiras e relatórios",
            "features": [
                # Financial Entries - todas
                "financial_entries.create",
                "financial_entries.read",
                "financial_entries.update",
                "financial_entries.delete",

                # Payment Modalities - todas
                "payment_modalities.create",
                "payment_modalities.read",
                "payment_modalities.update",
                "payment_modalities.delete",
                "payment_modalities.toggle",

                # Users - apenas visualização
                "users.read",

                # Reports - todas
                "reports.financial_summary",
                "reports.export",
            ]
        },
        {
            "name": "Usuário",
            "description": "Usuário com acesso básico para visualização e criação",
            "features": [
                # Financial Entries - criar e visualizar
                "financial_entries.create",
                "financial_entries.read",

                # Payment Modalities - visualizar
                "payment_modalities.read",

                # Reports - visualizar
                "reports.financial_summary",
            ]
        },
        {
            "name": "Visualizador",
            "description": "Acesso somente leitura para relatórios e dados",
            "features": [
                # Financial Entries - apenas visualizar
                "financial_entries.read",

                # Payment Modalities - apenas visualizar
                "payment_modalities.read",

                # Reports - apenas visualizar
                "reports.financial_summary",
            ]
        },
    ]

    print(f"🌱 Iniciando seed de roles para empresa {company_id}...\n")

    created_count = 0
    existing_count = 0

    for role_data in default_roles:
        # Verifica se já existe
        existing = role_repo.find_by_name(role_data["name"], company_id)

        if existing:
            print(f"⏭️  Role '{role_data['name']}' já existe")
            existing_count += 1
        else:
            # Mapeia códigos de features para IDs
            feature_ids = []
            missing_features = []

            for feature_code in role_data["features"]:
                feature_id = feature_dict.get(feature_code)
                if feature_id:
                    feature_ids.append(feature_id)
                else:
                    missing_features.append(feature_code)

            if missing_features:
                print(f"⚠️  Features não encontradas para '{role_data['name']}': {', '.join(missing_features)}")

            # Cria a role
            role = Role(
                name=role_data["name"],
                company_id=company_id,
                feature_ids=feature_ids
            )

            created_role = role_repo.create(role)
            print(f"✅ Role '{role_data['name']}' criada com {len(feature_ids)} features")
            created_count += 1

    print(f"\n📊 Resumo:")
    print(f"   ✅ Criadas: {created_count}")
    print(f"   ⏭️  Já existiam: {existing_count}")
    print(f"   📦 Total: {len(default_roles)}")
    print(f"\n🎉 Seed de roles concluído!")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Erro: company_id é obrigatório")
        print("Uso: python scripts/seed_roles.py <company_id>")
        sys.exit(1)

    company_id = sys.argv[1]
    seed_roles(company_id)
