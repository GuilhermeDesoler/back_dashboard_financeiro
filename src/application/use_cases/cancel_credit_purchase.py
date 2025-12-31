"""
Caso de uso para cancelar uma compra no crediário
"""
from src.domain.repositories.credit_purchase_repository import CreditPurchaseRepository
from src.domain.repositories.credit_installment_repository import CreditInstallmentRepository


class CancelCreditPurchase:
    """
    Caso de uso para cancelar uma compra no crediário.

    Ao cancelar:
    1. Marca a compra como cancelada
    2. Cancela todas as parcelas pendentes/atrasadas
    3. Mantém histórico das parcelas já pagas
    """

    def __init__(
        self,
        credit_purchase_repository: CreditPurchaseRepository,
        credit_installment_repository: CreditInstallmentRepository
    ):
        self.credit_purchase_repository = credit_purchase_repository
        self.credit_installment_repository = credit_installment_repository

    def execute(self, credit_purchase_id: str) -> dict:
        """
        Cancela uma compra no crediário.

        Args:
            credit_purchase_id: ID da compra a ser cancelada

        Returns:
            dict: Compra cancelada

        Raises:
            ValueError: Se a compra não for encontrada ou já estiver cancelada
        """
        # Buscar a compra
        credit_purchase = self.credit_purchase_repository.find_by_id(credit_purchase_id)
        if not credit_purchase:
            raise ValueError("Compra não encontrada")

        # Verificar se já está cancelada
        if credit_purchase.status == "cancelado":
            raise ValueError("Compra já está cancelada")

        # Cancelar a compra
        credit_purchase.cancel()
        updated_purchase = self.credit_purchase_repository.update(credit_purchase)

        # Cancelar todas as parcelas pendentes/atrasadas
        canceled_count = self.credit_installment_repository.cancel_all_by_credit_purchase(
            credit_purchase_id
        )

        return {
            "credit_purchase": updated_purchase.to_dict(),
            "canceled_installments": canceled_count
        }
