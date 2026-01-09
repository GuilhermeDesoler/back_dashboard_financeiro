"""
Script completo para importação de TODOS os dados da São Luiz Calçados
Importa: Vendas, Despesas, Crediário, Boletos, Empréstimos, Investimentos e Saldos Bancários

IMPORTANTE: Execute este script com a empresa já criada pelo seed_sao_luiz.py
Company ID: 9848381a-7b78-4d3e-a781-cd94fdcf8236
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database.mongo_connection import MongoConnection
from src.domain.entities.financial_entry import FinancialEntry
from src.domain.entities.account import Account
from src.domain.entities.installment import Installment
from src.domain.entities.bank_limit import BankLimit

# Configurações
COMPANY_ID = "9848381a-7b78-4d3e-a781-cd94fdcf8236"
COMPANY_DB_NAME = "cmp_57280b31_db"  # Database correto da São Luiz


class SaoLuizImporter:
    """Importador completo para todos os dados da São Luiz Calçados"""

    def __init__(self, mongo_conn: MongoConnection):
        self.db = mongo_conn.get_tenant_db(COMPANY_DB_NAME)
        self.modality_map = {}
        self.stats = {
            'vendas': {'created': 0, 'errors': 0, 'total_value': 0.0},
            'despesas': {'created': 0, 'errors': 0, 'total_value': 0.0},
            'crediario': {'created': 0, 'errors': 0, 'total_value': 0.0},
            'boletos': {'created': 0, 'errors': 0, 'total_value': 0.0},
            'emprestimos': {'created': 0, 'errors': 0, 'total_value': 0.0},
            'investimentos': {'created': 0, 'errors': 0, 'total_value': 0.0},
            'limites': {'created': 0, 'errors': 0}
        }

    def load_modalities(self):
        """Carrega modalidades existentes"""
        modalities = self.db['payment_modalities'].find({'is_active': True})
        self.modality_map = {m['name']: m['_id'] for m in modalities}
        print(f"✅ Carregadas {len(self.modality_map)} modalidades")

    @staticmethod
    def parse_brazilian_currency(value_str: str) -> float:
        """Converte R$ 1.234,56 para 1234.56"""
        if not value_str or not value_str.strip():
            return 0.0
        value_str = value_str.replace("R$", "").strip().replace(".", "").replace(",", ".")
        try:
            return float(value_str)
        except:
            return 0.0

    @staticmethod
    def parse_date(date_str: str) -> Optional[datetime]:
        """Parse DD/MM/YYYY para datetime"""
        if not date_str or not date_str.strip():
            return None
        try:
            return datetime.strptime(date_str.strip(), "%d/%m/%Y")
        except:
            return None

    @staticmethod
    def fix_encoding(text: str) -> str:
        """Corrige problemas de encoding UTF-8"""
        return (text
                .replace('Ã©', 'é')
                .replace('Ã¡', 'á')
                .replace('Ã­', 'í')
                .replace('Ã³', 'ó')
                .replace('Ãº', 'ú')
                .replace('Ã§', 'ç')
                .replace('Ã£', 'ã'))

    def import_vendas_csv(self, csv_path: str):
        """
        Importa vendas (Novembro, Dezembro, Janeiro)
        Formato: Linha 0 = total, Linha 1 = datas, Linha 2 = vazio, Linha 3+ = valores e modalidades
        """
        print(f"\n📊 Importando vendas de: {csv_path}")

        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')

        # Parse header com datas
        header_line = lines[1].strip().split(',')
        dates = []
        date_indices = []

        for i in range(0, len(header_line), 2):
            if i < len(header_line):
                date_str = header_line[i].strip().replace('"', '')
                if '/' in date_str and date_str.count('/') == 2:
                    date_obj = self.parse_date(date_str)
                    if date_obj:
                        dates.append(date_obj)
                        date_indices.append(i)

        print(f"  📅 Encontradas {len(dates)} datas")

        # Processar linhas de dados
        data_lines = lines[3:]

        for line in data_lines:
            if not line.strip():
                continue

            parts = line.split(',')

            for date_idx, date_obj in enumerate(dates):
                col_idx = date_indices[date_idx]

                if col_idx < len(parts) and col_idx + 1 < len(parts):
                    value_str = parts[col_idx].strip().replace('"', '')
                    modality_str = parts[col_idx + 1].strip().replace('"', '')

                    # Limpar encoding
                    modality_str = self.fix_encoding(modality_str)

                    if not value_str or not modality_str or modality_str == "Modalidade":
                        continue

                    if not value_str.startswith('R$'):
                        continue

                    value = self.parse_brazilian_currency(value_str)

                    if value > 0:
                        modality_id = self.modality_map.get(modality_str)

                        if not modality_id:
                            print(f"  ⚠️  Modalidade não encontrada: {modality_str}")
                            self.stats['vendas']['errors'] += 1
                            continue

                        # Criar entrada financeira
                        try:
                            # Buscar cor da modalidade
                            modality = self.db['payment_modalities'].find_one({'_id': modality_id})
                            modality_color = modality.get('color', '#9333EA') if modality else '#9333EA'

                            is_credit_plan = (modality_str == "Crediário" or
                                            modality_str == "Recebimento Crediario")

                            entry = FinancialEntry(
                                value=value,
                                date=date_obj,
                                modality_id=str(modality_id),
                                modality_name=modality_str,
                                modality_color=modality_color,
                                type="received",
                                entry_type="normal",
                                is_credit_plan=is_credit_plan,
                                created_at=datetime.now(),
                                updated_at=datetime.now()
                            )

                            self.db['financial_entries'].insert_one(entry.to_dict())
                            self.stats['vendas']['created'] += 1
                            self.stats['vendas']['total_value'] += value

                        except Exception as e:
                            print(f"  ❌ Erro ao criar venda: {e}")
                            self.stats['vendas']['errors'] += 1

        print(f"  ✅ Vendas importadas: {self.stats['vendas']['created']}")
        print(f"  💰 Valor total: R$ {self.stats['vendas']['total_value']:,.2f}")

    def import_despesas_csv(self, csv_path: str):
        """
        Importa despesas (2025 ou 2026)
        Formato: Colunas = meses, Linhas = Data, Descrição, Valor, Status
        """
        print(f"\n💸 Importando despesas de: {csv_path}")

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Cada linha pode ter múltiplos meses
                for month_col, data in row.items():
                    if month_col.strip() == "" or not data.strip():
                        continue

                    # Assumindo formato: Data | Descrição | Valor | Status
                    # TODO: Ajustar baseado no formato real do CSV
                    pass

        print(f"  ✅ Despesas importadas: {self.stats['despesas']['created']}")

    def import_crediario_csv(self, csv_path: str):
        """
        Importa dados de crediário (2025 ou 2026)
        Formato: Por mês com colunas Data, venda, recebido, em aberto
        """
        print(f"\n💳 Importando crediário de: {csv_path}")

        # Determinar ano pelo nome do arquivo
        year = 2026 if "2026" in csv_path else 2025

        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')

        # Linha 1 tem os nomes dos meses
        month_line = lines[1].strip().split(',')

        # Mapear meses para números
        month_map = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marÃ§o': 3, 'marco': 3,
            'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }

        # Identificar posições dos meses (cada mês tem 4 colunas: Data, venda, recebido, em aberto)
        months_info = []
        for i, cell in enumerate(month_line):
            cell_clean = cell.strip().lower()
            if cell_clean in month_map:
                months_info.append({
                    'name': cell_clean,
                    'month_num': month_map[cell_clean],
                    'col_start': i
                })

        print(f"  📅 Encontrados {len(months_info)} meses")

        # Pegar modalidade Crediário
        crediario_modality = self.db['payment_modalities'].find_one({'name': 'Crediário'})
        if not crediario_modality:
            print("  ⚠️  Modalidade 'Crediário' não encontrada")
            return

        modality_id = str(crediario_modality['_id'])
        modality_color = crediario_modality.get('color', '#9333EA')

        # Processar linhas de dados (pulando linhas 0, 1, 2, 3 que são headers/totais)
        data_lines = lines[4:]

        for line in data_lines:
            if not line.strip():
                continue

            parts = line.split(',')

            # Para cada mês
            for month_info in months_info:
                col_idx = month_info['col_start']

                # Verificar se temos dados suficientes
                if col_idx + 3 >= len(parts):
                    continue

                day_str = parts[col_idx].strip()
                venda_str = parts[col_idx + 1].strip().replace('"', '')
                recebido_str = parts[col_idx + 2].strip().replace('"', '')
                em_aberto_str = parts[col_idx + 3].strip().replace('"', '')

                # Se não tem dia, pular
                if not day_str or not day_str.isdigit():
                    continue

                day = int(day_str)
                venda = self.parse_brazilian_currency(venda_str)

                # Criar entrada apenas se houve venda
                if venda > 0:
                    try:
                        # Criar data
                        date_obj = datetime(year, month_info['month_num'], day)

                        # Criar entrada financeira do tipo crediário
                        entry = FinancialEntry(
                            value=venda,
                            date=date_obj,
                            modality_id=modality_id,
                            modality_name="Crediário",
                            modality_color=modality_color,
                            type="receivable",  # A receber
                            entry_type="normal",
                            is_credit_plan=True,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )

                        self.db['financial_entries'].insert_one(entry.to_dict())
                        self.stats['crediario']['created'] += 1
                        self.stats['crediario']['total_value'] += venda

                    except Exception as e:
                        print(f"  ❌ Erro ao criar crediário: {e}")
                        self.stats['crediario']['errors'] += 1

        print(f"  ✅ Crediário importado: {self.stats['crediario']['created']}")
        print(f"  💰 Valor total: R$ {self.stats['crediario']['total_value']:,.2f}")

    def import_boletos_csv(self, csv_path: str):
        """
        Importa boletos/contas a pagar (2025 ou 2026)
        Formato: Por mês com valores por dia
        """
        print(f"\n🧾 Importando boletos de: {csv_path}")

        # Determinar ano pelo nome do arquivo
        year = 2026 if "2026" in csv_path else 2025

        with open(csv_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.strip().split('\n')

        # Linha 1 tem os nomes dos meses
        month_line = lines[1].strip().split(',')

        # Mapear meses para números
        month_map = {
            'janeiro': 1, 'fevereiro': 2, 'março': 3, 'marÃ§o': 3, 'marco': 3,
            'abril': 4, 'maio': 5, 'junho': 6, 'julho': 7, 'agosto': 8,
            'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
        }

        # Identificar posições dos meses (cada mês tem 2 colunas: nome e valor)
        months_info = []
        for i, cell in enumerate(month_line):
            cell_clean = cell.strip().lower()
            if cell_clean in month_map:
                months_info.append({
                    'name': cell_clean,
                    'month_num': month_map[cell_clean],
                    'col_start': i
                })

        print(f"  📅 Encontrados {len(months_info)} meses")

        # Processar linhas de dados (pulando linhas 0, 1, 2 que são headers/totais)
        data_lines = lines[3:]

        for line in data_lines:
            if not line.strip():
                continue

            parts = line.split(',')

            # Para cada mês
            for month_info in months_info:
                col_idx = month_info['col_start']

                # Verificar se temos dados suficientes (dia e valor)
                if col_idx + 1 >= len(parts):
                    continue

                day_str = parts[col_idx].strip()
                valor_str = parts[col_idx + 1].strip().replace('"', '')

                # Se não tem dia ou não é número, pular
                if not day_str or not day_str.isdigit():
                    continue

                day = int(day_str)
                valor = self.parse_brazilian_currency(valor_str)

                # Criar boleto apenas se há valor
                if valor > 0:
                    try:
                        # Criar data
                        date_obj = datetime(year, month_info['month_num'], day)

                        # Criar Account tipo boleto
                        account = Account(
                            value=valor,
                            date=date_obj,
                            description=f"Boleto {day:02d}/{month_info['month_num']:02d}/{year}",
                            type="boleto",
                            paid=False,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )

                        self.db['accounts'].insert_one(account.to_dict())
                        self.stats['boletos']['created'] += 1
                        self.stats['boletos']['total_value'] += valor

                    except Exception as e:
                        print(f"  ❌ Erro ao criar boleto: {e}")
                        self.stats['boletos']['errors'] += 1

        print(f"  ✅ Boletos importados: {self.stats['boletos']['created']}")
        print(f"  💰 Valor total: R$ {self.stats['boletos']['total_value']:,.2f}")

    def import_emprestimos_csv(self, csv_path: str):
        """
        Importa empréstimos
        Formato: Banco, Saldo
        """
        print(f"\n💰 Importando empréstimos de: {csv_path}")

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                banco = row.get('Banco', '').strip()
                saldo_str = row.get('Saldo', '').strip()

                if not banco or not saldo_str:
                    continue

                saldo = self.parse_brazilian_currency(saldo_str)

                if saldo > 0:
                    try:
                        # Criar como entrada financeira tipo empréstimo
                        entry = FinancialEntry(
                            value=saldo,
                            date=datetime.now(),
                            modality_id="emprestimo",
                            modality_name=f"Empréstimo {banco}",
                            modality_color="#EF4444",
                            type="received",
                            entry_type="emprestimo",
                            is_credit_plan=False,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )

                        self.db['financial_entries'].insert_one(entry.to_dict())
                        self.stats['emprestimos']['created'] += 1
                        self.stats['emprestimos']['total_value'] += saldo

                    except Exception as e:
                        print(f"  ❌ Erro ao criar empréstimo: {e}")
                        self.stats['emprestimos']['errors'] += 1

        print(f"  ✅ Empréstimos importados: {self.stats['emprestimos']['created']}")
        print(f"  💰 Valor total: R$ {self.stats['emprestimos']['total_value']:,.2f}")

    def import_investimentos_csv(self, csv_path: str):
        """
        Importa investimentos
        Formato: Banco, Valor, Tipo, Objetivo
        """
        print(f"\n📈 Importando investimentos de: {csv_path}")

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                banco = row.get('Banco', '').strip()
                valor_str = row.get('Valor', '').strip()
                tipo = row.get('Tipo', '').strip()
                objetivo = row.get('Objetivo', '').strip()

                if not banco or not valor_str:
                    continue

                valor = self.parse_brazilian_currency(valor_str)

                if valor > 0:
                    try:
                        descricao = f"{tipo} - {objetivo}" if tipo and objetivo else banco

                        # Criar como Account tipo investment
                        account = Account(
                            value=valor,
                            date=datetime.now(),
                            description=descricao,
                            type="investment",
                            paid=False,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )

                        self.db['accounts'].insert_one(account.to_dict())
                        self.stats['investimentos']['created'] += 1
                        self.stats['investimentos']['total_value'] += valor

                    except Exception as e:
                        print(f"  ❌ Erro ao criar investimento: {e}")
                        self.stats['investimentos']['errors'] += 1

        print(f"  ✅ Investimentos importados: {self.stats['investimentos']['created']}")
        print(f"  💰 Valor total: R$ {self.stats['investimentos']['total_value']:,.2f}")

    def import_saldos_limites_csv(self, csv_path: str):
        """
        Importa saldos e limites bancários
        Formato: Banco, Tipo Limite, Valor, Taxa
        """
        print(f"\n🏦 Importando saldos e limites de: {csv_path}")

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                banco = row.get('Banco', '').strip()
                tipo = row.get('Tipo', '').strip()
                limite_str = row.get('Limite', '') or row.get('Valor', '')
                limite_str = limite_str.strip()

                if not banco or not limite_str:
                    continue

                limite = self.parse_brazilian_currency(limite_str)

                if limite > 0:
                    try:
                        # Criar limite bancário
                        bank_limit = BankLimit(
                            bank_name=banco,
                            limit_type=tipo,
                            total_limit=limite,
                            used_amount=0.0,
                            available_amount=limite,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )

                        self.db['bank_limits'].insert_one(bank_limit.to_dict())
                        self.stats['limites']['created'] += 1

                    except Exception as e:
                        print(f"  ❌ Erro ao criar limite: {e}")
                        self.stats['limites']['errors'] += 1

        print(f"  ✅ Limites importados: {self.stats['limites']['created']}")

    def print_summary(self):
        """Imprime resumo completo da importação"""
        print("\n" + "="*60)
        print("📊 RESUMO COMPLETO DA IMPORTAÇÃO")
        print("="*60)

        for tipo, stats in self.stats.items():
            print(f"\n{tipo.upper()}:")
            print(f"  ✅ Criados: {stats['created']}")
            if 'total_value' in stats:
                print(f"  💰 Valor: R$ {stats['total_value']:,.2f}")
            if stats.get('errors', 0) > 0:
                print(f"  ❌ Erros: {stats['errors']}")

        print("\n" + "="*60)


def main():
    """Executa importação completa"""
    print("🚀 Iniciando importação completa - São Luiz Calçados")
    print(f"📁 Company ID: {COMPANY_ID}")
    print(f"🗄️  Database: {COMPANY_DB_NAME}")
    print("="*60)

    # Conectar ao banco
    mongo_conn = MongoConnection()
    importer = SaoLuizImporter(mongo_conn)

    # Carregar modalidades
    importer.load_modalities()

    # Diretório base dos CSVs
    csv_dir = Path("/Users/primum/financeiros/back_dashboard_financeiro")

    # Importar vendas
    vendas_files = [
        "Cópia de Financeiro São Luiz Calçados - Vendas Novembro_25.csv",
        "Cópia de Financeiro São Luiz Calçados - Vendas Dezembro_25.csv",
        "Cópia de Financeiro São Luiz Calçados - Vendas Janeiro_26.csv"
    ]

    for vendas_file in vendas_files:
        vendas_path = csv_dir / vendas_file
        if vendas_path.exists():
            importer.import_vendas_csv(str(vendas_path))
        else:
            print(f"⚠️  Arquivo não encontrado: {vendas_path}")

    # Importar empréstimos
    emprestimos_path = csv_dir / "Cópia de Financeiro São Luiz Calçados - Emprestimos.csv"
    if emprestimos_path.exists():
        importer.import_emprestimos_csv(str(emprestimos_path))

    # Importar investimentos
    investimentos_path = csv_dir / "Cópia de Financeiro São Luiz Calçados - Investimentos.csv"
    if investimentos_path.exists():
        importer.import_investimentos_csv(str(investimentos_path))

    # Importar saldos e limites
    saldos_path = csv_dir / "Cópia de Financeiro São Luiz Calçados - Saldos e Taxas.csv"
    if saldos_path.exists():
        importer.import_saldos_limites_csv(str(saldos_path))

    # Importar crediário
    crediario_files = [
        "Cópia de Financeiro São Luiz Calçados - Crediário 2025.csv",
        "Cópia de Financeiro São Luiz Calçados - Crediário 2026.csv"
    ]

    for crediario_file in crediario_files:
        crediario_path = csv_dir / crediario_file
        if crediario_path.exists():
            importer.import_crediario_csv(str(crediario_path))
        else:
            print(f"⚠️  Arquivo não encontrado: {crediario_path}")

    # Importar boletos
    boletos_files = [
        "Cópia de Financeiro São Luiz Calçados - Boletos 2025.csv",
        "Cópia de Financeiro São Luiz Calçados - Boletos 2026.csv"
    ]

    for boletos_file in boletos_files:
        boletos_path = csv_dir / boletos_file
        if boletos_path.exists():
            importer.import_boletos_csv(str(boletos_path))
        else:
            print(f"⚠️  Arquivo não encontrado: {boletos_path}")

    # TODO: Adicionar importação de despesas quando o CSV estiver disponível

    # Resumo final
    importer.print_summary()

    print("\n✅ Importação completa finalizada!")


if __name__ == "__main__":
    main()
