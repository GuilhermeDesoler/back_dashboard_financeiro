"""
Script de seed para São Luiz Calçados
Cria empresa, modalidades e importa transações do CSV

Para executar: python scripts/seed_sao_luiz.py
"""

import sys
import os
from datetime import datetime
from decimal import Decimal
import csv

# Add project root and src to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.database.mongo_connection import MongoConnection
from src.domain.entities.company import Company
from src.domain.entities.payment_modality import PaymentModality
from src.domain.entities.financial_entry import FinancialEntry
from src.infra.repositories.mongo_company_repository import MongoCompanyRepository
from src.infra.repositories.mongo_payment_modality_repository import MongoPaymentModalityRepository
from src.infra.repositories.mongo_financial_entry_repository import MongoFinancialEntryRepository
import uuid


# Modalidades da São Luiz Calçados
MODALITIES = [
    {"name": "Pix Sicredi", "color": "#00C853"},
    {"name": "Pix Sicoob", "color": "#00E676"},
    {"name": "Débito Sicredi", "color": "#2196F3"},
    {"name": "Débito Sicoob", "color": "#03A9F4"},
    {"name": "Crédito Av Sicredi", "color": "#FF9800"},
    {"name": "Crédito Av Sicoob", "color": "#FFB74D"},
    {"name": "Dinheiro", "color": "#4CAF50"},
    {"name": "Crediário", "color": "#9C27B0"},
    {"name": "Recebimento Crediario", "color": "#BA68C8"},
    {"name": "BonusCred", "color": "#E91E63"},
    {"name": "Parcelado 2 a 4 Sicredi", "color": "#FF5722"},
    {"name": "Parcelado 5 a 6 Sicredi", "color": "#F44336"},
    {"name": "Parcelado 2 a 4 Sicoob", "color": "#FF6F00"},
    {"name": "Parcelado 5 a 6 Sicoob", "color": "#FF8F00"},
]


def parse_brazilian_currency(value_str: str) -> Decimal:
    """Convert R$ 1.234,56 to Decimal(1234.56)"""
    if not value_str or not value_str.strip():
        return Decimal('0')
    value_str = value_str.replace("R$", "").strip().replace(".", "").replace(",", ".")
    try:
        return Decimal(value_str)
    except:
        return Decimal('0')


def parse_date(date_str: str) -> datetime:
    """Parse DD/MM/YYYY to datetime"""
    return datetime.strptime(date_str.strip(), "%d/%m/%Y")


def create_company():
    """Cria a empresa São Luiz Calçados"""
    print("\n🏢 Criando empresa São Luiz Calçados...")

    db_connection = MongoConnection()
    shared_db = db_connection.shared_db
    collection = shared_db['companies']
    repository = MongoCompanyRepository(collection)

    # Verificar se já existe
    existing = collection.find_one({'name': 'São Luiz Calçados'})
    if existing:
        print("⚠️  Empresa já existe, usando ID existente")
        return str(existing['_id'])

    # Criar nova empresa
    company = Company(
        name="São Luiz Calçados",
        cnpj=None,
        phone=None,
        plan="basic",
        is_active=True
    )

    created_company = repository.create(company)
    print(f"✅ Empresa criada: {created_company.name} (ID: {created_company.id})")

    return created_company.id


def seed_modalities(company_id: str):
    """Cria modalidades de pagamento"""
    print(f"\n💳 Criando modalidades de pagamento para empresa {company_id}...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "São Luiz Calçados")
    collection = tenant_db['payment_modalities']
    repository = MongoPaymentModalityRepository(collection)

    modality_map = {}

    for idx, mod_data in enumerate(MODALITIES, 1):
        modality = PaymentModality(
            name=mod_data['name'],
            color=mod_data['color'],
            bank_name="",
            fee_percentage=0.0,
            rental_fee=0.0,
            is_active=True,
            is_credit_plan=False,
            allows_anticipation=False,
            allows_credit_payment=False
        )

        created = repository.create(modality)
        modality_map[mod_data['name']] = created.id
        print(f"   {idx:2}. ✅ {mod_data['name']:30} | {mod_data['color']}")

    print(f"\n✅ {len(modality_map)} modalidades criadas!")
    return modality_map


def import_transactions(company_id: str, modality_map: dict, csv_file_path: str):
    """Importa transações do CSV"""
    print(f"\n📊 Importando transações do CSV...")

    if not os.path.exists(csv_file_path):
        print(f"❌ Arquivo não encontrado: {csv_file_path}")
        print("   Coloque o arquivo CSV no diretório: /Users/primum/financeiros/dashboard_financeiro/")
        return

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "São Luiz Calçados")
    collection = tenant_db['financial_entries']
    repository = MongoFinancialEntryRepository(collection)

    # Ler CSV
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Parse header para pegar datas
    header_line = lines[1].strip().split(',')
    dates = []
    date_indices = []

    for i in range(0, len(header_line), 2):
        if i < len(header_line):
            date_str = header_line[i].strip().replace('"', '')
            if '/' in date_str and date_str.count('/') == 2:
                try:
                    date_obj = parse_date(date_str)
                    dates.append(date_obj)
                    date_indices.append(i)
                except:
                    pass

    print(f"   📅 {len(dates)} datas encontradas: {dates[0].strftime('%d/%m/%Y')} a {dates[-1].strftime('%d/%m/%Y')}")

    total_transactions = 0
    total_value = Decimal('0')
    skipped = 0

    # Processar linhas (pular primeiras 3: total, header, vazio)
    for line_idx in range(3, len(lines)):
        line = lines[line_idx].strip()
        if not line:
            continue

        parts = line.split(',')

        # Processar cada coluna de data
        for date_idx, date_obj in enumerate(dates):
            col_idx = date_indices[date_idx]

            if col_idx < len(parts) and col_idx + 1 < len(parts):
                value_str = parts[col_idx].strip().replace('"', '')
                modality_str = parts[col_idx + 1].strip().replace('"', '')

                # Limpar encoding
                modality_str = (modality_str
                    .replace('Ã©', 'é')
                    .replace('Ã¡', 'á')
                    .replace('Ã­', 'í'))

                # Pular se não tem valor ou modalidade
                if not value_str or not modality_str or modality_str == "Modalidade":
                    continue

                # Pular se não começa com R$
                if not value_str.startswith('R$'):
                    continue

                value = parse_brazilian_currency(value_str)

                if value > 0:
                    modality_id = modality_map.get(modality_str)

                    if not modality_id:
                        skipped += 1
                        continue

                    try:
                        # Criar financial entry
                        entry = FinancialEntry(
                            date=date_obj,
                            value=float(value),
                            description=f"Venda - {modality_str}",
                            entry_type="receita",
                            modality_id=modality_id
                        )

                        repository.create(entry)

                        total_transactions += 1
                        total_value += value

                        # Progress a cada 50 transações
                        if total_transactions % 50 == 0:
                            print(f"   ⏳ {total_transactions} transações importadas...")

                    except Exception as e:
                        print(f"   ⚠️  Erro ao importar: {str(e)}")

    # Resumo
    print(f"\n✅ Importação concluída!")
    print(f"   📊 Transações: {total_transactions}")
    print(f"   💰 Total: R$ {total_value:,.2f}")
    print(f"   ⏭️  Puladas: {skipped}")


def main():
    """Função principal"""
    print("=" * 80)
    print("SEED - SÃO LUIZ CALÇADOS")
    print("=" * 80)

    # Caminho do CSV
    csv_file = "/Users/primum/financeiros/dashboard_financeiro/Cópia de Financeiro São Luiz Calçados - Vendas Dezembro_25.csv"

    try:
        # 1. Criar empresa
        company_id = create_company()

        # 2. Criar modalidades
        modality_map = seed_modalities(company_id)

        # 3. Importar transações
        import_transactions(company_id, modality_map, csv_file)

        print("\n" + "=" * 80)
        print("✅ SEED COMPLETO!")
        print("=" * 80)
        print(f"\n📋 Empresa: São Luiz Calçados")
        print(f"   ID: {company_id}")
        print(f"\n💳 Modalidades: {len(modality_map)}")
        print(f"\n📊 Use 'Impersonar' no dashboard para visualizar os dados")
        print("\n" + "=" * 80)

    except Exception as e:
        print(f"\n❌ Erro durante seed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
