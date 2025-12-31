"""
Caso de uso para criar uma nova compra no crediário
"""
from datetime import datetime, timedelta
from typing import List

from src.domain.entities.credit_purchase import CreditPurchase
from src.domain.entities.credit_installment import CreditInstallment
from src.domain.repositories.credit_purchase_repository import CreditPurchaseRepository
from src.domain.repositories.credit_installment_repository import CreditInstallmentRepository


class CreateCreditPurchase:
    """Caso de uso para criar uma compra no crediário com suas parcelas"""

    def __init__(
        self,
        credit_purchase_repository: CreditPurchaseRepository,
        credit_installment_repository: CreditInstallmentRepository
    ):
        self.credit_purchase_repository = credit_purchase_repository
        self.credit_installment_repository = credit_installment_repository

    def execute(
        self,
        pagante_nome: str,
        descricao_compra: str,
        valor_total: float,
        numero_parcelas: int,
        data_inicio_pagamento: datetime,
        registrado_por_user_id: str,
        registrado_por_nome: str,
        pagante_documento: str = None,
        pagante_telefone: str = None,
        valor_entrada: float = 0.0,
        intervalo_dias: int = 30,
        taxa_juros_mensal: float = 0.0
    ) -> dict:
        """
        Cria uma nova compra no crediário e gera automaticamente suas parcelas.

        Args:
            pagante_nome: Nome do cliente/pagante
            descricao_compra: Descrição do que foi comprado
            valor_total: Valor total da compra
            numero_parcelas: Quantidade de parcelas
            data_inicio_pagamento: Data do primeiro vencimento
            registrado_por_user_id: ID do usuário que está criando
            registrado_por_nome: Nome do usuário que está criando
            pagante_documento: CPF/CNPJ do pagante
            pagante_telefone: Telefone de contato
            valor_entrada: Valor da entrada paga
            intervalo_dias: Dias entre parcelas
            taxa_juros_mensal: Taxa de juros mensal

        Returns:
            dict: Compra criada com suas parcelas
        """
        # Criar a compra
        credit_purchase = CreditPurchase(
            pagante_nome=pagante_nome,
            descricao_compra=descricao_compra,
            valor_total=valor_total,
            numero_parcelas=numero_parcelas,
            data_inicio_pagamento=data_inicio_pagamento,
            registrado_por_user_id=registrado_por_user_id,
            registrado_por_nome=registrado_por_nome,
            pagante_documento=pagante_documento,
            pagante_telefone=pagante_telefone,
            valor_entrada=valor_entrada,
            intervalo_dias=intervalo_dias,
            taxa_juros_mensal=taxa_juros_mensal,
        )

        # Validar
        credit_purchase.validate()

        # Salvar a compra
        created_purchase = self.credit_purchase_repository.create(credit_purchase)

        # Gerar as parcelas automaticamente
        installments = self._generate_installments(created_purchase)

        # Salvar todas as parcelas
        created_installments = self.credit_installment_repository.create_many(installments)

        # Retornar compra com parcelas
        return {
            "credit_purchase": created_purchase.to_dict(),
            "installments": [inst.to_dict() for inst in created_installments]
        }

    def _generate_installments(self, credit_purchase: CreditPurchase) -> List[CreditInstallment]:
        """
        Gera as parcelas automaticamente baseado nos dados da compra.

        Args:
            credit_purchase: Compra criada

        Returns:
            Lista de parcelas geradas
        """
        installments = []

        # Calcular valor a parcelar (total - entrada)
        valor_a_parcelar = credit_purchase.valor_total - credit_purchase.valor_entrada

        # Calcular valor de cada parcela
        valor_parcela_base = valor_a_parcelar / credit_purchase.numero_parcelas

        # Gerar cada parcela
        for i in range(credit_purchase.numero_parcelas):
            numero_parcela = i + 1

            # Calcular data de vencimento
            dias_offset = i * credit_purchase.intervalo_dias
            data_vencimento = credit_purchase.data_inicio_pagamento + timedelta(days=dias_offset)

            # Criar a parcela
            installment = CreditInstallment(
                credit_purchase_id=credit_purchase.id,
                numero_parcela=numero_parcela,
                valor_parcela=round(valor_parcela_base, 2),
                data_vencimento=data_vencimento,
                valor_juros=0.0,
                valor_multa=0.0,
                status="pendente"
            )

            installments.append(installment)

        # Ajustar última parcela para compensar arredondamentos
        total_parcelas = sum(inst.valor_parcela for inst in installments)
        diferenca = round(valor_a_parcelar - total_parcelas, 2)

        if diferenca != 0:
            installments[-1].valor_parcela += diferenca

        return installments
