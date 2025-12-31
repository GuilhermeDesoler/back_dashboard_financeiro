"""
Caso de uso para desfazer o pagamento de uma parcela do crediário
"""
from src.domain.repositories.credit_installment_repository import CreditInstallmentRepository
from src.domain.repositories.credit_purchase_repository import CreditPurchaseRepository
from src.domain.repositories.finacial_entry_repository import FinancialEntryRepository


class UnpayCreditInstallment:
    """
    Caso de uso para desfazer o pagamento de uma parcela do crediário.

    Ao desfazer o pagamento:
    1. Remove o FinancialEntry vinculado
    2. Atualiza a parcela removendo os dados de pagamento
    3. Recalcula o status da parcela (pendente ou atrasado)
    4. Reativa a compra se estava concluída
    """

    def __init__(
        self,
        credit_installment_repository: CreditInstallmentRepository,
        credit_purchase_repository: CreditPurchaseRepository,
        financial_entry_repository: FinancialEntryRepository
    ):
        self.credit_installment_repository = credit_installment_repository
        self.credit_purchase_repository = credit_purchase_repository
        self.financial_entry_repository = financial_entry_repository

    def execute(self, installment_id: str) -> dict:
        """
        Desfaz o pagamento de uma parcela.

        Args:
            installment_id: ID da parcela cujo pagamento será desfeito

        Returns:
            dict: Parcela atualizada

        Raises:
            ValueError: Se a parcela não for encontrada ou não estiver paga
        """
        # Buscar a parcela
        installment = self.credit_installment_repository.find_by_id(installment_id)
        if not installment:
            raise ValueError("Parcela não encontrada")

        # Verificar se está paga
        if installment.status != "pago":
            raise ValueError("Apenas parcelas pagas podem ter o pagamento desfeito")

        # Remover o lançamento financeiro vinculado (se existir)
        if installment.financial_entry_id:
            self.financial_entry_repository.delete(installment.financial_entry_id)

        # Desfazer o pagamento na parcela
        installment.desfazer_pagamento()

        # Salvar a parcela atualizada
        updated_installment = self.credit_installment_repository.update(installment)

        # Reativar a compra se estava concluída
        credit_purchase = self.credit_purchase_repository.find_by_id(
            installment.credit_purchase_id
        )
        if credit_purchase and credit_purchase.status == "concluido":
            credit_purchase.reactivate()
            self.credit_purchase_repository.update(credit_purchase)

        return {
            "installment": updated_installment.to_dict()
        }
