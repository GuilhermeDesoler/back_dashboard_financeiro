"""
Script completo de seed com dados baseados nas tabelas fornecidas.
Inclui modalidades, limites bancários, lançamentos financeiros, crediários e pagamentos.

Para executar: python scripts/seed_complete_data.py
"""

import sys
import os
from datetime import datetime, timedelta
from decimal import Decimal

# Add project root and src to path
project_root = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'src'))

from src.database.mongo_connection import MongoConnection
from src.domain.entities.payment_modality import PaymentModality
from src.domain.entities.financial_entry import FinancialEntry
from src.domain.entities.installment import Installment
from src.domain.entities.account import Account
from src.domain.entities.bank_limit import BankLimit
from src.domain.entities.platform_settings import PlatformSettings
from src.infra.repositories.mongo_payment_modality_repository import MongoPaymentModalityRepository
from src.infra.repositories.mongo_financial_entry_repository import MongoFinancialEntryRepository
from src.infra.repositories.mongo_installment_repository import MongoInstallmentRepository
from src.infra.repositories.mongo_account_repository import MongoAccountRepository
from src.infra.repositories.mongo_bank_limit_repository import MongoBankLimitRepository
from src.infra.repositories.mongo_platform_settings_repository import MongoPlatformSettingsRepository
import uuid


def get_test_company_id():
    """Busca o ID da empresa de teste"""
    db_connection = MongoConnection()
    shared_db = db_connection.shared_db
    company = shared_db['companies'].find_one({'name': 'Empresa Teste Ltda'})
    if not company:
        print("❌ Empresa de teste não encontrada! Execute seed_all.py primeiro.")
        sys.exit(1)
    return str(company['_id'])


def clear_existing_data(company_id: str):
    """Limpa dados existentes da empresa"""
    print("\n🗑️  Limpando dados existentes...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")

    # Limpar collections
    tenant_db['payment_modalities'].delete_many({})
    tenant_db['financial_entries'].delete_many({})
    tenant_db['installments'].delete_many({})
    tenant_db['accounts'].delete_many({})
    tenant_db['bank_limits'].delete_many({})
    tenant_db['platform_settings'].delete_many({})

    print("✅ Dados limpos com sucesso!")


def seed_payment_modalities(company_id: str):
    """Cria modalidades de pagamento baseadas nas tabelas fornecidas"""
    print("\n💳 Criando modalidades de pagamento...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")
    collection = tenant_db['payment_modalities']
    repository = MongoPaymentModalityRepository(collection)

    # Modalidades baseadas na tabela fornecida
    modalities_data = [
        # PIX
        {
            'name': 'pix',
            'color': '#00D09C',
            'bank_name': 'sicredi',
            'fee_percentage': 0.0,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },
        {
            'name': 'pix',
            'color': '#00D09C',
            'bank_name': 'Sicoob',
            'fee_percentage': 0.0,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },
        {
            'name': 'pix',
            'color': '#00D09C',
            'bank_name': 'link sicredi',
            'fee_percentage': 0.0,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },

        # DÉBITO
        {
            'name': 'débito',
            'color': '#4A90E2',
            'bank_name': 'sicredi',
            'fee_percentage': 0.9,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },
        {
            'name': 'débito',
            'color': '#4A90E2',
            'bank_name': 'Sicoob',
            'fee_percentage': 0.9,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },
        {
            'name': 'débito',
            'color': '#4A90E2',
            'bank_name': 'link sicredi',
            'fee_percentage': 0.9,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },

        # CRÉDITO À VISTA
        {
            'name': 'crédito à vista',
            'color': '#FF6B6B',
            'bank_name': 'sicredi',
            'fee_percentage': 1.1,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },
        {
            'name': 'crédito à vista',
            'color': '#FF6B6B',
            'bank_name': 'Sicoob',
            'fee_percentage': 1.1,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },
        {
            'name': 'crédito à vista',
            'color': '#FF6B6B',
            'bank_name': 'link sicredi',
            'fee_percentage': 1.3,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },

        # CRÉDITO 2 A 6
        {
            'name': 'crédito 2 a 6',
            'color': '#FFA500',
            'bank_name': 'sicredi',
            'fee_percentage': 1.4,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },
        {
            'name': 'crédito 2 a 6',
            'color': '#FFA500',
            'bank_name': 'Sicoob',
            'fee_percentage': 1.4,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },
        {
            'name': 'crédito 2 a 6',
            'color': '#FFA500',
            'bank_name': 'link sicredi',
            'fee_percentage': 1.6,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },

        # CRÉDITO 7 A 12
        {
            'name': 'crédito 7 a 12',
            'color': '#9333EA',
            'bank_name': 'sicredi',
            'fee_percentage': 1.6,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },
        {
            'name': 'crédito 7 a 12',
            'color': '#9333EA',
            'bank_name': 'Sicoob',
            'fee_percentage': 1.6,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },
        {
            'name': 'crédito 7 a 12',
            'color': '#9333EA',
            'bank_name': 'link sicredi',
            'fee_percentage': 1.8,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': True,
            'allows_credit_payment': False,
        },

        # ANTECIPAÇÃO
        {
            'name': 'antecipação',
            'color': '#E91E63',
            'bank_name': 'sicredi',
            'fee_percentage': 1.7,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },
        {
            'name': 'antecipação',
            'color': '#E91E63',
            'bank_name': 'Sicoob',
            'fee_percentage': 1.59,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },
        {
            'name': 'antecipação',
            'color': '#E91E63',
            'bank_name': 'link sicredi',
            'fee_percentage': 1.79,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },

        # MÁQUINAS (crediário - permite parcelamento interno)
        {
            'name': 'máquinas',
            'color': '#795548',
            'bank_name': 'sicredi',
            'fee_percentage': 2.0,
            'rental_fee': 0.0,
            'is_credit_plan': True,  # Permite criar crediários
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },
        {
            'name': 'máquinas',
            'color': '#795548',
            'bank_name': 'Sicoob',
            'fee_percentage': 1.0,
            'rental_fee': 0.0,
            'is_credit_plan': True,  # Permite criar crediários
            'allows_anticipation': False,
            'allows_credit_payment': False,
        },

        # ALUGUEL (modalidade para recebimento de crediários)
        {
            'name': 'aluguel',
            'color': '#607D8B',
            'bank_name': 'sicredi',
            'fee_percentage': 0.0,
            'rental_fee': 0.0,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': True,  # Permite marcar como pagamento de crediário
        },
        {
            'name': 'aluguel',
            'color': '#607D8B',
            'bank_name': 'Sicoob',
            'fee_percentage': 0.0,
            'rental_fee': 56.90,
            'is_credit_plan': False,
            'allows_anticipation': False,
            'allows_credit_payment': True,  # Permite marcar como pagamento de crediário
        },
    ]

    created_modalities = []
    for mod_data in modalities_data:
        modality = PaymentModality(
            name=mod_data['name'],
            color=mod_data['color'],
            bank_name=mod_data['bank_name'],
            fee_percentage=mod_data['fee_percentage'],
            rental_fee=mod_data['rental_fee'],
            is_active=True,
            is_credit_plan=mod_data['is_credit_plan'],
            allows_anticipation=mod_data['allows_anticipation'],
            allows_credit_payment=mod_data['allows_credit_payment']
        )
        created = repository.create(modality)
        created_modalities.append(created)
        print(f"   ✓ {mod_data['name']} ({mod_data['bank_name']}) - Taxa: {mod_data['fee_percentage']}%")

    print(f"✅ {len(created_modalities)} modalidades criadas!")
    return created_modalities


def seed_bank_limits(company_id: str):
    """Cria limites bancários baseados na tabela fornecida"""
    print("\n🏦 Criando limites bancários...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")
    collection = tenant_db['bank_limits']
    repository = MongoBankLimitRepository(collection)

    bank_limits_data = [
        {
            'bank_name': 'Sicredi',
            'rotativo_available': 80000.00,
            'rotativo_used': 70000.00,
            'cheque_available': 5000.00,
            'cheque_used': 0.00,
        },
        {
            'bank_name': 'Sicoob',
            'rotativo_available': 30000.00,
            'rotativo_used': 0.00,
            'cheque_available': 0.00,
            'cheque_used': 0.00,
        },
    ]

    created_limits = []
    for limit_data in bank_limits_data:
        created = repository.create(
            bank_name=limit_data['bank_name'],
            rotativo_available=limit_data['rotativo_available'],
            rotativo_used=limit_data['rotativo_used'],
            cheque_available=limit_data['cheque_available'],
            cheque_used=limit_data['cheque_used']
        )
        created_limits.append(created)
        print(f"   ✓ {limit_data['bank_name']}: Rotativo R$ {limit_data['rotativo_available']:,.2f} (usado: R$ {limit_data['rotativo_used']:,.2f})")

    # Calcular totais
    total_available = sum(bl['rotativo_available'] + bl['cheque_available'] for bl in bank_limits_data)
    total_used = sum(bl['rotativo_used'] + bl['cheque_used'] for bl in bank_limits_data)
    provision = 2302.21  # Provisão de juros da tabela

    print(f"\n   📊 Total Disponível: R$ {total_available:,.2f}")
    print(f"   📊 Total em Uso: R$ {total_used:,.2f}")
    print(f"   📊 Provisão Juros: R$ {provision:,.2f}")

    print(f"✅ {len(created_limits)} limites bancários criados!")
    return created_limits


def seed_financial_entries(company_id: str, modalities: list):
    """Cria lançamentos financeiros de exemplo"""
    print("\n💰 Criando lançamentos financeiros de exemplo...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")
    collection = tenant_db['financial_entries']
    repository = MongoFinancialEntryRepository(collection)

    # Criar um mapa de modalidades para facilitar busca
    modalities_map = {}
    for mod in modalities:
        key = f"{mod.name}_{mod.bank_name}"
        modalities_map[key] = mod

    # Data base para os lançamentos (últimos 30 dias)
    base_date = datetime.now() - timedelta(days=30)

    entries_data = []

    # Exemplos de lançamentos variados ao longo do mês
    for day in range(0, 30, 3):  # A cada 3 dias
        current_date = base_date + timedelta(days=day)

        # PIX - vários ao longo do mês
        if day % 2 == 0:
            entries_data.append({
                'value': 150.00 + (day * 10),
                'date': current_date,
                'modality_key': 'pix_sicredi',
            })

        # Débito
        if day % 3 == 0:
            entries_data.append({
                'value': 85.50 + (day * 5),
                'date': current_date,
                'modality_key': 'débito_Sicoob',
            })

        # Crédito à vista
        if day % 4 == 0:
            entries_data.append({
                'value': 200.00 + (day * 15),
                'date': current_date,
                'modality_key': 'crédito à vista_sicredi',
            })

        # Crédito 2 a 6
        if day % 5 == 0:
            entries_data.append({
                'value': 350.00 + (day * 20),
                'date': current_date,
                'modality_key': 'crédito 2 a 6_link sicredi',
            })

        # Crédito 7 a 12
        if day % 6 == 0:
            entries_data.append({
                'value': 500.00 + (day * 25),
                'date': current_date,
                'modality_key': 'crédito 7 a 12_sicredi',
            })

        # Antecipação
        if day % 7 == 0:
            entries_data.append({
                'value': 1200.00 + (day * 30),
                'date': current_date,
                'modality_key': 'antecipação_Sicoob',
            })

    created_entries = []
    for entry_data in entries_data:
        modality = modalities_map.get(entry_data['modality_key'])
        if not modality:
            continue

        entry = FinancialEntry(
            value=entry_data['value'],
            date=entry_data['date'],
            modality_id=modality.id,
            modality_name=modality.name,
            modality_color=modality.color,
            type='received'
        )
        created = repository.create(entry)
        created_entries.append(created)

    print(f"✅ {len(created_entries)} lançamentos financeiros criados!")
    return created_entries


def seed_credit_plans(company_id: str, modalities: list):
    """Cria crediários (planos de crédito) com parcelas"""
    print("\n📋 Criando crediários (máquinas) com parcelas...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")

    entry_collection = tenant_db['financial_entries']
    entry_repository = MongoFinancialEntryRepository(entry_collection)

    installment_collection = tenant_db['installments']
    installment_repository = MongoInstallmentRepository(installment_collection)

    # Encontrar modalidades de máquinas (is_credit_plan=True)
    credit_plan_modalities = [m for m in modalities if m.is_credit_plan]

    if not credit_plan_modalities:
        print("⚠️  Nenhuma modalidade de crediário encontrada!")
        return []

    # Criar alguns crediários de exemplo
    credit_plans_data = [
        {
            'value': 3000.00,
            'date': datetime.now() - timedelta(days=60),
            'installments_count': 10,
            'start_date': datetime.now() - timedelta(days=30),
            'modality': credit_plan_modalities[0],  # máquinas sicredi
            'paid_installments': 2,  # Primeiras 2 parcelas já pagas
        },
        {
            'value': 5000.00,
            'date': datetime.now() - timedelta(days=90),
            'installments_count': 12,
            'start_date': datetime.now() - timedelta(days=60),
            'modality': credit_plan_modalities[0],
            'paid_installments': 4,  # Primeiras 4 parcelas já pagas
        },
        {
            'value': 2400.00,
            'date': datetime.now() - timedelta(days=45),
            'installments_count': 8,
            'start_date': datetime.now() - timedelta(days=15),
            'modality': credit_plan_modalities[1] if len(credit_plan_modalities) > 1 else credit_plan_modalities[0],  # máquinas Sicoob
            'paid_installments': 1,  # Primeira parcela paga
        },
        {
            'value': 6000.00,
            'date': datetime.now() - timedelta(days=120),
            'installments_count': 15,
            'start_date': datetime.now() - timedelta(days=90),
            'modality': credit_plan_modalities[0],
            'paid_installments': 6,  # Primeiras 6 parcelas já pagas
        },
    ]

    created_entries = []
    total_installments_created = 0

    for plan_data in credit_plans_data:
        # Criar entrada financeira principal
        entry = FinancialEntry(
            value=plan_data['value'],
            date=plan_data['date'],
            modality_id=plan_data['modality'].id,
            modality_name=plan_data['modality'].name,
            modality_color=plan_data['modality'].color,
            type='receivable'  # A receber (crediário)
        )
        created_entry = entry_repository.create(entry)
        created_entries.append(created_entry)

        # Criar parcelas
        installment_value = plan_data['value'] / plan_data['installments_count']

        for i in range(plan_data['installments_count']):
            installment_number = i + 1
            due_date = plan_data['start_date'] + timedelta(days=30 * i)

            is_paid = installment_number <= plan_data['paid_installments']
            payment_date = due_date if is_paid else None

            installment = Installment(
                financial_entry_id=created_entry.id,
                installment_number=installment_number,
                total_installments=plan_data['installments_count'],
                amount=installment_value,
                due_date=due_date,
                is_paid=is_paid,
                payment_date=payment_date
            )
            installment_repository.create(installment)
            total_installments_created += 1

        paid_count = plan_data['paid_installments']
        pending_count = plan_data['installments_count'] - paid_count
        print(f"   ✓ Crediário R$ {plan_data['value']:,.2f} em {plan_data['installments_count']}x de R$ {installment_value:,.2f}")
        print(f"     ({paid_count} pagas, {pending_count} pendentes)")

    print(f"✅ {len(created_entries)} crediários criados com {total_installments_created} parcelas!")
    return created_entries


def seed_credit_payments(company_id: str, modalities: list, installment_repo):
    """Cria lançamentos de pagamento de crediário"""
    print("\n💳 Criando pagamentos de crediário...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")
    entry_collection = tenant_db['financial_entries']
    entry_repository = MongoFinancialEntryRepository(entry_collection)

    # Encontrar modalidades que aceitam pagamento de crediário
    payment_modalities = [m for m in modalities if m.allows_credit_payment]

    if not payment_modalities:
        print("⚠️  Nenhuma modalidade de pagamento de crediário encontrada!")
        return []

    # Buscar parcelas pagas para criar lançamentos correspondentes
    all_installments = installment_repo.find_all()
    paid_installments = [i for i in all_installments if i.is_paid]

    created_entries = []

    # Criar um lançamento para cada parcela paga
    for installment in paid_installments[:10]:  # Limitar a 10 para exemplo
        # Escolher modalidade de pagamento aleatoriamente
        import random
        payment_modality = random.choice(payment_modalities)

        entry = FinancialEntry(
            value=installment.amount,
            date=installment.payment_date or installment.due_date,
            modality_id=payment_modality.id,
            modality_name=payment_modality.name,
            modality_color=payment_modality.color,
            type='received'  # Recebido (pagamento de crediário)
        )
        created = entry_repository.create(entry)
        created_entries.append(created)

    print(f"✅ {len(created_entries)} pagamentos de crediário criados!")
    return created_entries


def seed_accounts(company_id: str):
    """Cria contas de exemplo (boletos, pagamentos, investimentos)"""
    print("\n📄 Criando contas (boletos, pagamentos, investimentos)...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")
    collection = tenant_db['accounts']
    repository = MongoAccountRepository(collection)

    accounts_data = [
        # Boletos
        {
            'value': 1500.00,
            'date': datetime.now() - timedelta(days=15),
            'description': 'Boleto - Fornecedor ABC Ltda',
            'type': 'boleto',
        },
        {
            'value': 850.00,
            'date': datetime.now() - timedelta(days=10),
            'description': 'Boleto - Energia Elétrica',
            'type': 'boleto',
        },
        {
            'value': 450.00,
            'date': datetime.now() - timedelta(days=5),
            'description': 'Boleto - Internet/Telefone',
            'type': 'boleto',
        },

        # Pagamentos diversos
        {
            'value': 3200.00,
            'date': datetime.now() - timedelta(days=20),
            'description': 'Pagamento - Folha de Salários',
            'type': 'payment',
        },
        {
            'value': 1200.00,
            'date': datetime.now() - timedelta(days=12),
            'description': 'Pagamento - Aluguel Escritório',
            'type': 'payment',
        },
        {
            'value': 650.00,
            'date': datetime.now() - timedelta(days=8),
            'description': 'Pagamento - Contador',
            'type': 'payment',
        },

        # Investimentos
        {
            'value': 5000.00,
            'date': datetime.now() - timedelta(days=25),
            'description': 'Investimento - CDB Banco Sicredi',
            'type': 'investment',
        },
        {
            'value': 3000.00,
            'date': datetime.now() - timedelta(days=18),
            'description': 'Investimento - Tesouro Direto',
            'type': 'investment',
        },
        {
            'value': 2000.00,
            'date': datetime.now() - timedelta(days=7),
            'description': 'Investimento - Fundo de Investimento',
            'type': 'investment',
        },
    ]

    created_accounts = []
    for account_data in accounts_data:
        account = Account(
            value=account_data['value'],
            date=account_data['date'],
            description=account_data['description'],
            type=account_data['type']
        )
        created = repository.create(account)
        created_accounts.append(created)
        print(f"   ✓ {account_data['type'].upper()}: {account_data['description']} - R$ {account_data['value']:,.2f}")

    print(f"✅ {len(created_accounts)} contas criadas!")
    return created_accounts


def seed_platform_settings(company_id: str):
    """Cria configurações da plataforma"""
    print("\n⚙️  Configurando plataforma...")

    db_connection = MongoConnection()
    tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")
    collection = tenant_db['platform_settings']
    repository = MongoPlatformSettingsRepository(collection)

    # get_settings() cria se não existir
    settings = repository.get_settings()
    settings.is_anticipation_enabled = True
    updated = repository.update_settings(settings)

    print(f"   ✓ Antecipação: {'Habilitada' if updated.is_anticipation_enabled else 'Desabilitada'}")
    print("✅ Configurações criadas!")
    return updated


def main():
    """Executa todo o processo de seed"""
    print("="*60)
    print("🌱 SEED COMPLETO DE DADOS - DASHBOARD FINANCEIRO")
    print("="*60)

    try:
        # Buscar empresa de teste
        company_id = get_test_company_id()
        print(f"\n📍 Empresa: {company_id}")

        # Confirmar limpeza
        response = input("\n⚠️  Deseja limpar os dados existentes? (s/N): ")
        if response.lower() == 's':
            clear_existing_data(company_id)

        # Executar seeds
        modalities = seed_payment_modalities(company_id)
        bank_limits = seed_bank_limits(company_id)
        entries = seed_financial_entries(company_id, modalities)
        credit_plans = seed_credit_plans(company_id, modalities)

        # Criar repositório de installments para buscar parcelas
        db_connection = MongoConnection()
        tenant_db = db_connection.get_tenant_db(company_id, "Empresa Teste Ltda")
        installment_collection = tenant_db['installments']
        installment_repo = MongoInstallmentRepository(installment_collection)
        credit_payments = seed_credit_payments(company_id, modalities, installment_repo)

        accounts = seed_accounts(company_id)
        settings = seed_platform_settings(company_id)

        print("\n" + "="*60)
        print("✅ SEED COMPLETO EXECUTADO COM SUCESSO!")
        print("="*60)
        print(f"\n📊 Resumo:")
        print(f"   • {len(modalities)} modalidades de pagamento")
        print(f"   • {len(bank_limits)} limites bancários")
        print(f"   • {len(entries)} lançamentos financeiros")
        print(f"   • {len(credit_plans)} crediários com parcelas")
        print(f"   • {len(credit_payments)} pagamentos de crediário")
        print(f"   • {len(accounts)} contas (boletos/pagamentos/investimentos)")
        print(f"   • Configurações da plataforma")

        print("\n🎉 Dados prontos para uso!")

    except Exception as e:
        print(f"\n❌ Erro durante seed: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
