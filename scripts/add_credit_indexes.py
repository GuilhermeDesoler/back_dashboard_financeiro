"""
Script para adicionar índices das collections de crediário em bancos de dados existentes.

Execução:
    python scripts/add_credit_indexes.py
"""
import os
import sys
from pathlib import Path

# Adicionar o diretório raiz ao PYTHONPATH
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from dotenv import load_dotenv
from src.database import MongoConnection, get_shared_db

# Carregar variáveis de ambiente
load_dotenv()


def add_credit_indexes_to_tenant_db(tenant_db):
    """
    Adiciona índices das collections de crediário em um banco de dados de tenant.

    Args:
        tenant_db: Database do tenant
    """
    print(f"  Adicionando índices em {tenant_db.name}...")

    # Índices para credit_purchases
    print("    - credit_purchases...")
    tenant_db["credit_purchases"].create_index("id", unique=True)
    tenant_db["credit_purchases"].create_index("status")
    tenant_db["credit_purchases"].create_index("pagante_nome")
    tenant_db["credit_purchases"].create_index([("created_at", -1)])

    # Índices para credit_installments
    print("    - credit_installments...")
    tenant_db["credit_installments"].create_index("id", unique=True)
    tenant_db["credit_installments"].create_index("credit_purchase_id")
    tenant_db["credit_installments"].create_index("status")
    tenant_db["credit_installments"].create_index("data_vencimento")
    tenant_db["credit_installments"].create_index([("data_vencimento", 1)])
    tenant_db["credit_installments"].create_index("financial_entry_id")
    # Índice composto para queries do dashboard
    tenant_db["credit_installments"].create_index([
        ("data_vencimento", 1),
        ("status", 1)
    ])

    print(f"  ✅ Índices adicionados em {tenant_db.name}")


def main():
    """Função principal"""
    print("🔧 Adicionando índices de crediário nos bancos existentes...\n")

    # Conectar ao MongoDB
    MongoConnection()
    shared_db = get_shared_db()

    # Buscar todas as empresas
    companies = list(shared_db["companies"].find({}))
    print(f"📊 Encontradas {len(companies)} empresas\n")

    if not companies:
        print("⚠️  Nenhuma empresa encontrada. Certifique-se de que o banco está populado.")
        return

    # Para cada empresa, adicionar índices no seu banco
    mongo_client = MongoConnection()._client

    for company in companies:
        company_id = company["id"]
        company_name = company["name"]

        print(f"🏢 Processando empresa: {company_name} (ID: {company_id})")

        # Calcular nome do banco (mesmo algoritmo do TenantDatabaseManager)
        import hashlib
        short_hash = hashlib.md5(company_id.encode()).hexdigest()[:8]
        db_name = f"cmp_{short_hash}_db"

        # Obter o banco
        tenant_db = mongo_client[db_name]

        # Adicionar índices
        add_credit_indexes_to_tenant_db(tenant_db)
        print()

    print("✅ Migração concluída com sucesso!")
    print("\n📝 Próximos passos:")
    print("   1. Reiniciar a aplicação")
    print("   2. Verificar se os endpoints de crediário estão funcionando")
    print("   3. Testar a criação de uma compra no crediário")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Erro durante a migração: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
