"""
Script para verificar onde estão os dados da São Luiz Calçados
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.mongo_connection import MongoConnection


def main():
    conn = MongoConnection()

    # Lista todos os databases
    print("🔍 Procurando dados da São Luiz Calçados em todos os databases...")
    print()

    databases = conn.client.list_database_names()

    # Filtra databases relevantes
    relevant_dbs = [db for db in databases if 'luiz' in db.lower() or 'calcad' in db.lower() or 'cmp_' in db or 'company_' in db]

    print(f"📋 Databases relevantes encontrados: {len(relevant_dbs)}")
    print()

    for db_name in relevant_dbs:
        print(f"📦 Database: {db_name}")
        db = conn.client[db_name]

        # Verifica financial_entries
        if 'financial_entries' in db.list_collection_names():
            count = db['financial_entries'].count_documents({})
            if count > 0:
                print(f"   ✅ financial_entries: {count} documentos")
                # Mostra exemplos
                sample = db['financial_entries'].find_one()
                if sample:
                    print(f"      Exemplo: {sample.get('date')}, R$ {sample.get('value')}")

        # Verifica accounts
        if 'accounts' in db.list_collection_names():
            count = db['accounts'].count_documents({})
            if count > 0:
                print(f"   ✅ accounts: {count} documentos")
                sample = db['accounts'].find_one()
                if sample:
                    print(f"      Exemplo: {sample.get('date')}, R$ {sample.get('value')}")

        # Verifica payment_modalities
        if 'payment_modalities' in db.list_collection_names():
            count = db['payment_modalities'].count_documents({})
            if count > 0:
                print(f"   ✅ payment_modalities: {count} documentos")

        print()


if __name__ == '__main__':
    main()
