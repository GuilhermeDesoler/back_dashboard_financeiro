"""
Caso de uso para obter dados do dashboard de crediário
"""
from datetime import datetime
from typing import Optional

from src.domain.repositories.credit_installment_repository import CreditInstallmentRepository
from src.domain.repositories.credit_purchase_repository import CreditPurchaseRepository


class GetCreditDashboard:
    """Caso de uso para obter dados agregados do dashboard de crediário"""

    def __init__(
        self,
        credit_installment_repository: CreditInstallmentRepository,
        credit_purchase_repository: CreditPurchaseRepository
    ):
        self.credit_installment_repository = credit_installment_repository
        self.credit_purchase_repository = credit_purchase_repository

    def execute(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None
    ) -> dict:
        """
        Obtém dados do dashboard agrupados por data de vencimento.

        Args:
            start_date: Data inicial
            end_date: Data final
            status: Filtro de status (opcional)

        Returns:
            dict: Dados do dashboard com parcelas agrupadas por data
        """
        # Obter parcelas agrupadas por data
        dashboard_data = self.credit_installment_repository.get_dashboard_by_date(
            start_date=start_date,
            end_date=end_date,
            status=status
        )

        # Obter totais gerais
        totals = self.credit_installment_repository.get_totals(
            start_date=start_date,
            end_date=end_date
        )

        # Adicionar totais ao dashboard
        dashboard_data["summary"] = totals

        # Enriquecer cada parcela com dados da compra
        for day_data in dashboard_data.get("installments_by_date", []):
            for installment in day_data.get("installments", []):
                # Buscar dados básicos da compra
                credit_purchase = self.credit_purchase_repository.find_by_id(
                    installment["credit_purchase_id"]
                )
                if credit_purchase:
                    installment["pagante_nome"] = credit_purchase.pagante_nome
                    installment["descricao_compra"] = credit_purchase.descricao_compra
                    installment["pagante_telefone"] = credit_purchase.pagante_telefone

        return dashboard_data
