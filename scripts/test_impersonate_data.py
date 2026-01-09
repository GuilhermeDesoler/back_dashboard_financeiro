"""
Script para testar se o impersonate está funcionando corretamente
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.mongo_connection import MongoConnection


def main():
    conn = MongoConnection()
    shared_db = conn.shared_db

    # Busca a empresa São Luiz Calçados
    company = shared_db['companies'].find_one({'name': 'São Luiz Calçados'})

    if not company:
        print("❌ Empresa São Luiz Calçados não encontrada!")
        return

    print("✅ Empresa encontrada")
    print(f"   Nome: {company['name']}")
    print(f"   ID: {company.get('id')}")
    print(f"   DB Name: {company.get('db_name')}")
    print()

    # Testa get_tenant_db com o company_id
    company_id = company.get('id') or str(company['_id'])
    print(f"🔍 Testando get_tenant_db('{company_id}')...")

    try:
        tenant_db = conn.get_tenant_db(company_id)
        print(f"✅ Database conectado: {tenant_db.name}")
        print()

        # Verifica os dados
        print("📊 Dados no database:")

        financial_entries_count = tenant_db['financial_entries'].count_documents({})
        print(f"   financial_entries: {financial_entries_count} documentos")

        if financial_entries_count > 0:
            sample = tenant_db['financial_entries'].find_one()
            print(f"      Exemplo: {sample.get('date')}, R$ {sample.get('value')}")

        accounts_count = tenant_db['accounts'].count_documents({})
        print(f"   accounts: {accounts_count} documentos")

        if accounts_count > 0:
            sample = tenant_db['accounts'].find_one()
            print(f"      Exemplo: {sample.get('date')}, R$ {sample.get('value')}")

        modalities_count = tenant_db['payment_modalities'].count_documents({})
        print(f"   payment_modalities: {modalities_count} documentos")

        print()

        if financial_entries_count > 0 or accounts_count > 0:
            print("🎉 SUCESSO! Os dados estão acessíveis através do company_id!")
            print("   O impersonate deve funcionar corretamente agora.")
        else:
            print("⚠️  Nenhum dado encontrado no database!")

    except Exception as e:
        print(f"❌ Erro ao acessar database: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
