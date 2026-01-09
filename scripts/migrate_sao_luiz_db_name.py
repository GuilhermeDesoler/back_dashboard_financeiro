"""
Script para migrar São Luiz Calçados para usar nome da empresa como database name
"""
import sys
from pathlib import Path

# Adiciona o diretório raiz ao path
sys.path.append(str(Path(__file__).parent.parent))

from src.database.mongo_connection import MongoConnection
import re


def sanitize_company_name(name: str) -> str:
    """Sanitiza o nome da empresa para usar como nome do database"""
    safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name.lower())
    safe_name = re.sub(r'_+', '_', safe_name)  # Remove underscores duplicados
    safe_name = safe_name.strip('_')  # Remove underscores das pontas
    return f"company_{safe_name}"


def main():
    conn = MongoConnection()
    shared_db = conn.shared_db

    # Busca a empresa São Luiz Calçados
    company = shared_db['companies'].find_one({'name': 'São Luiz Calçados'})

    if not company:
        print("❌ Empresa São Luiz Calçados não encontrada!")
        return

    print(f"✅ Empresa encontrada: {company['name']}")
    company_id = company.get('id') or str(company['_id'])
    print(f"   ID: {company_id}")

    # Gera o novo db_name baseado no nome da empresa
    new_db_name = sanitize_company_name(company['name'])
    print(f"\n📦 Novo database name: {new_db_name}")

    # Database antigo (baseado em hash)
    import hashlib
    short_hash = hashlib.md5(company_id.encode()).hexdigest()[:8]
    old_db_name = f"cmp_{short_hash}_db"
    print(f"📦 Database antigo: {old_db_name}")

    # Atualiza o documento da empresa com o db_name
    print(f"\n🔄 Atualizando documento da empresa...")

    # Usa o critério correto para buscar (_id ou id)
    query = {'_id': company['_id']} if '_id' in company else {'id': company_id}
    result = shared_db['companies'].update_one(
        query,
        {'$set': {'db_name': new_db_name}}
    )

    if result.modified_count > 0:
        print("✅ Empresa atualizada com sucesso!")
    else:
        print("ℹ️  Empresa já tinha o db_name configurado")

    # Migra os dados do database antigo para o novo
    old_db = conn.client[old_db_name]
    new_db = conn.client[new_db_name]

    print(f"\n🔄 Migrando dados de {old_db_name} para {new_db_name}...")

    # Lista todas as collections do database antigo
    collections = old_db.list_collection_names()

    if not collections:
        print("⚠️  Database antigo não tem collections!")
        return

    print(f"📋 Collections encontradas: {collections}")

    total_docs = 0
    for collection_name in collections:
        # Pula collections do sistema
        if collection_name.startswith('system.'):
            continue

        old_collection = old_db[collection_name]
        new_collection = new_db[collection_name]

        # Conta documentos
        count = old_collection.count_documents({})
        if count == 0:
            print(f"   ⏭️  {collection_name}: 0 documentos (pulando)")
            continue

        print(f"   🔄 {collection_name}: {count} documentos...")

        # Copia todos os documentos
        docs = list(old_collection.find({}))
        if docs:
            # Remove _id para evitar conflitos
            for doc in docs:
                if '_id' in doc:
                    del doc['_id']

            new_collection.insert_many(docs)
            total_docs += len(docs)
            print(f"   ✅ {collection_name}: {len(docs)} documentos migrados")

    print(f"\n✅ Migração concluída!")
    print(f"   Total de documentos migrados: {total_docs}")

    # Recria índices no novo database
    print(f"\n🔧 Criando índices no novo database...")

    # Índices para financial_entries
    if 'financial_entries' in collections:
        new_db['financial_entries'].create_index('date')
        new_db['financial_entries'].create_index('modality_id')
        new_db['financial_entries'].create_index([('date', -1)])
        print("   ✅ Índices criados para financial_entries")

    # Índices para payment_modalities
    if 'payment_modalities' in collections:
        try:
            new_db['payment_modalities'].create_index(
                'name',
                unique=True,
                collation={'locale': 'pt', 'strength': 2}
            )
            new_db['payment_modalities'].create_index('is_active')
            print("   ✅ Índices criados para payment_modalities")
        except Exception as e:
            print(f"   ⚠️  Erro ao criar índice único: {e}")

    # Índices para accounts
    if 'accounts' in collections:
        new_db['accounts'].create_index('date')
        new_db['accounts'].create_index('type')
        new_db['accounts'].create_index('paid')
        print("   ✅ Índices criados para accounts")

    print(f"\n🎉 Migração completa!")
    print(f"\n📊 Resumo:")
    print(f"   Empresa: {company['name']}")
    print(f"   Novo database: {new_db_name}")
    print(f"   Documentos migrados: {total_docs}")
    print(f"\n⚠️  IMPORTANTE: O database antigo ({old_db_name}) ainda existe.")
    print(f"   Você pode deletá-lo manualmente após verificar que tudo está funcionando.")


if __name__ == '__main__':
    main()
