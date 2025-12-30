"""
Script para popular features do sistema

Execute: python scripts/seed_features.py
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import get_shared_db
from src.domain.entities import Feature
from src.infra.repositories import MongoFeatureRepository
from datetime import datetime


def seed_features():
    """Cria as features padrão do sistema"""

    shared_db = get_shared_db()
    feature_repo = MongoFeatureRepository(shared_db["features"])

    # Define as features do sistema
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

        # Company Settings (Admin only)
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

    print("🌱 Iniciando seed de features...")

    created_count = 0
    existing_count = 0

    for feature in system_features:
        # Verifica se já existe
        existing = feature_repo.find_by_code(feature.code)

        if existing:
            print(f"⏭️  Feature '{feature.code}' já existe")
            existing_count += 1
        else:
            feature_repo.create(feature)
            print(f"✅ Feature '{feature.code}' criada")
            created_count += 1

    print(f"\n📊 Resumo:")
    print(f"   ✅ Criadas: {created_count}")
    print(f"   ⏭️  Já existiam: {existing_count}")
    print(f"   📦 Total: {len(system_features)}")
    print(f"\n🎉 Seed de features concluído!")


if __name__ == "__main__":
    seed_features()
