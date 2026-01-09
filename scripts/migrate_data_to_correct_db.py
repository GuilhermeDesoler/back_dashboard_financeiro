"""
Script para migrar dados de cmp_afa2734c_db para company_s_o_luiz_cal_ados
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.mongo_connection import MongoConnection


def main():
    conn = MongoConnection()

    source_db_name = 'cmp_afa2734c_db'
    target_db_name = 'company_s_o_luiz_cal_ados'

    source_db = conn.client[source_db_name]
    target_db = conn.client[target_db_name]

    print(f"🔄 Migrando dados de {source_db_name} para {target_db_name}...")
    print()

    # Lista collections a migrar
    collections_to_migrate = ['financial_entries', 'accounts', 'payment_modalities']

    total_docs = 0

    for collection_name in collections_to_migrate:
        source_collection = source_db[collection_name]
        target_collection = target_db[collection_name]

        # Conta documentos na origem
        source_count = source_collection.count_documents({})
        if source_count == 0:
            print(f"⏭️  {collection_name}: 0 documentos (pulando)")
            continue

        print(f"📋 {collection_name}:")
        print(f"   Origem: {source_count} documentos")

        # Limpa a collection de destino
        target_collection.delete_many({})
        print(f"   🧹 Collection de destino limpa")

        # Copia todos os documentos
        docs = list(source_collection.find({}))
        if docs:
            # Remove _id para evitar conflitos
            for doc in docs:
                if '_id' in doc:
                    del doc['_id']

            target_collection.insert_many(docs)
            total_docs += len(docs)
            print(f"   ✅ {len(docs)} documentos migrados")

        print()

    print(f"✅ Migração concluída!")
    print(f"   Total de documentos migrados: {total_docs}")

    # Recria índices
    print(f"\n🔧 Criando índices...")

    # Índices para financial_entries
    target_db['financial_entries'].create_index('date')
    target_db['financial_entries'].create_index('modality_id')
    target_db['financial_entries'].create_index([('date', -1)])
    print("   ✅ Índices criados para financial_entries")

    # Índices para payment_modalities
    # Remove índice antigo se existir
    try:
        target_db['payment_modalities'].drop_indexes()
    except:
        pass

    # Remove duplicatas (mantém apenas a primeira ocorrência de cada nome)
    modalities = list(target_db['payment_modalities'].find({}))
    seen_names = set()
    duplicates_to_remove = []

    for mod in modalities:
        name_lower = mod['name'].lower()
        if name_lower in seen_names:
            duplicates_to_remove.append(mod['_id'])
        else:
            seen_names.add(name_lower)

    if duplicates_to_remove:
        target_db['payment_modalities'].delete_many({'_id': {'$in': duplicates_to_remove}})
        print(f"   🧹 {len(duplicates_to_remove)} duplicatas removidas")

    target_db['payment_modalities'].create_index(
        'name',
        unique=True,
        collation={'locale': 'pt', 'strength': 2}
    )
    target_db['payment_modalities'].create_index('is_active')
    print("   ✅ Índices criados para payment_modalities")

    # Índices para accounts
    target_db['accounts'].create_index('date')
    target_db['accounts'].create_index('type')
    target_db['accounts'].create_index('paid')
    print("   ✅ Índices criados para accounts")

    print(f"\n🎉 Migração completa!")
    print(f"\n📊 Resumo:")
    print(f"   Origem: {source_db_name}")
    print(f"   Destino: {target_db_name}")
    print(f"   Documentos migrados: {total_docs}")

    # Verifica o resultado
    print(f"\n🔍 Verificando dados migrados:")
    print(f"   financial_entries: {target_db['financial_entries'].count_documents({})}")
    print(f"   accounts: {target_db['accounts'].count_documents({})}")
    print(f"   payment_modalities: {target_db['payment_modalities'].count_documents({})}")


if __name__ == '__main__':
    main()
