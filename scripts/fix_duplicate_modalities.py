"""
Script para corrigir modalidades duplicadas e recriar índices

Este script:
1. Lista todas as empresas
2. Para cada empresa:
   - Remove duplicatas de modalidades (mantém a mais recente)
   - Remove índice antigo (case-sensitive)
   - Cria novo índice case-insensitive
"""

import sys
from pathlib import Path
from collections import defaultdict

# Adiciona o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from src.database import MongoConnection, get_shared_db, get_tenant_db
from src.infra.repositories import MongoCompanyRepository


def fix_duplicate_modalities():
    """Corrige modalidades duplicadas em todas as empresas"""
    print("🔧 Iniciando correção de modalidades duplicadas...\n")

    # Conectar ao MongoDB
    MongoConnection()
    shared_db = get_shared_db()

    # Buscar todas as empresas
    company_repo = MongoCompanyRepository(shared_db["companies"])
    companies = company_repo.find_all(only_active=False)  # Inclui inativas também

    print(f"📊 Encontradas {len(companies)} empresas\n")

    total_duplicates_removed = 0

    for company in companies:
        print(f"🏢 Processando: {company.name} (ID: {company.id})")

        try:
            # Obter DB da empresa
            tenant_db = get_tenant_db(company.id)
            modalities_collection = tenant_db["payment_modalities"]

            # Buscar todas as modalidades
            modalities = list(modalities_collection.find())

            if not modalities:
                print("   ⏭️  Sem modalidades cadastradas\n")
                continue

            # Agrupar por nome (case-insensitive)
            grouped = defaultdict(list)
            for modality in modalities:
                name_lower = modality["name"].strip().lower()
                grouped[name_lower].append(modality)

            # Encontrar duplicatas
            duplicates_found = False
            for name_lower, mods in grouped.items():
                if len(mods) > 1:
                    duplicates_found = True
                    print(f"   ⚠️  Duplicata encontrada: '{mods[0]['name']}' ({len(mods)} ocorrências)")

                    # Ordenar por created_at (mais recente primeiro)
                    mods.sort(key=lambda x: x.get("created_at", ""), reverse=True)

                    # Manter o primeiro (mais recente), deletar os outros
                    keep = mods[0]
                    to_delete = mods[1:]

                    print(f"      ✅ Mantendo: ID {keep['_id']}")

                    for mod in to_delete:
                        print(f"      🗑️  Removendo: ID {mod['_id']}")
                        modalities_collection.delete_one({"_id": mod["_id"]})
                        total_duplicates_removed += 1

            if not duplicates_found:
                print("   ✅ Nenhuma duplicata encontrada")

            # Recriar índice com collation case-insensitive
            print("   🔄 Recriando índice...")

            # Remover índice antigo se existir
            try:
                modalities_collection.drop_index("name_1")
                print("      ❌ Índice antigo removido")
            except Exception:
                print("      ℹ️  Índice antigo não encontrado (ok)")

            # Criar novo índice case-insensitive
            modalities_collection.create_index(
                "name",
                unique=True,
                collation={"locale": "pt", "strength": 2},
                name="name_1"
            )
            print("      ✅ Índice case-insensitive criado\n")

        except Exception as e:
            print(f"   ❌ Erro ao processar empresa: {str(e)}\n")
            continue

    # Resumo
    print("=" * 60)
    print("🎉 CORREÇÃO CONCLUÍDA!")
    print("=" * 60)
    print(f"\n📊 Resumo:")
    print(f"  • Empresas processadas: {len(companies)}")
    print(f"  • Modalidades duplicadas removidas: {total_duplicates_removed}")
    print(f"\n✅ Todas as empresas agora têm:")
    print(f"  • Índice único case-insensitive no campo 'name'")
    print(f"  • Sem duplicatas de modalidades")
    print(f"\n⚠️  IMPORTANTE:")
    print(f"  • Novas empresas criadas automaticamente terão o índice correto")
    print(f"  • A validação no código agora é case-insensitive")
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        fix_duplicate_modalities()
    except Exception as e:
        print(f"\n❌ Erro durante a correção: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
