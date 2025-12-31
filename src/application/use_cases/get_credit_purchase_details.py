"""
Caso de uso para obter detalhes completos de uma compra no crediário
"""
from typing import Optional

from src.domain.repositories.credit_purchase_repository import CreditPurchaseRepository
from src.domain.repositories.credit_installment_repository import CreditInstallmentRepository


class GetCreditPurchaseDetails:
    """Caso de uso para obter todos os detalhes de uma compra com suas parcelas"""

    def __init__(
        self,
        credit_purchase_repository: CreditPurchaseRepository,
        credit_installment_repository: CreditInstallmentRepository
    ):
        self.credit_purchase_repository = credit_purchase_repository
        self.credit_installment_repository = credit_installment_repository

    def execute(self, credit_purchase_id: str) -> Optional[dict]:
        """
        Busca uma compra pelo ID com todas suas parcelas e dados calculados.

        Args:
            credit_purchase_id: ID da compra

        Returns:
            dict: Dados completos da compra ou None se não encontrada
        """
        # Buscar a compra
        credit_purchase = self.credit_purchase_repository.find_by_id(credit_purchase_id)
        if not credit_purchase:
            return None

        # Buscar todas as parcelas
        installments = self.credit_installment_repository.find_by_credit_purchase(
            credit_purchase_id
        )

        # Calcular totais
        total_pago = sum(
            inst.get_valor_total() for inst in installments if inst.status == "pago"
        )
        total_pendente = sum(
            inst.get_valor_total() for inst in installments
            if inst.status in ["pendente", "atrasado"]
        )
        parcelas_pagas = sum(1 for inst in installments if inst.status == "pago")
        parcelas_atrasadas = sum(1 for inst in installments if inst.status == "atrasado")

        # Calcular percentual pago
        valor_a_parcelar = credit_purchase.valor_total - credit_purchase.valor_entrada
        if valor_a_parcelar > 0:
            percentual_pago = round((total_pago / valor_a_parcelar) * 100, 2)
        else:
            percentual_pago = 100.0

        # Montar resposta
        return {
            **credit_purchase.to_dict(),
            "total_pago": total_pago,
            "total_pendente": total_pendente,
            "parcelas_pagas": parcelas_pagas,
            "parcelas_atrasadas": parcelas_atrasadas,
            "percentual_pago": percentual_pago,
            "installments": [inst.to_dict() for inst in installments]
        }
