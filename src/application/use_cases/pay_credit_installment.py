"""
Caso de uso para registrar o pagamento de uma parcela do crediário
"""
from datetime import datetime
from typing import Optional

from src.domain.entities.financial_entry import FinancialEntry
from src.domain.repositories.credit_installment_repository import CreditInstallmentRepository
from src.domain.repositories.credit_purchase_repository import CreditPurchaseRepository
from src.domain.repositories.finacial_entry_repository import FinancialEntryRepository
from src.domain.repositories.payment_modality_repository import PaymentModalityRepository


class PayCreditInstallment:
    """
    Caso de uso para registrar o pagamento de uma parcela do crediário.

    Ao pagar uma parcela:
    1. Atualiza a parcela (status, data_pagamento, etc.)
    2. Cria um FinancialEntry automaticamente
    3. Vincula os dois registros
    4. Verifica se todas as parcelas foram pagas para marcar a compra como concluída
    """

    def __init__(
        self,
        credit_installment_repository: CreditInstallmentRepository,
        credit_purchase_repository: CreditPurchaseRepository,
        financial_entry_repository: FinancialEntryRepository,
        payment_modality_repository: PaymentModalityRepository
    ):
        self.credit_installment_repository = credit_installment_repository
        self.credit_purchase_repository = credit_purchase_repository
        self.financial_entry_repository = financial_entry_repository
        self.payment_modality_repository = payment_modality_repository

    def execute(
        self,
        installment_id: str,
        data_pagamento: datetime,
        pago_por_user_id: str,
        pago_por_nome: str,
        modality_id: str,
        valor_juros: float = 0.0,
        valor_multa: float = 0.0,
        observacao: str = ""
    ) -> dict:
        """
        Registra o pagamento de uma parcela.

        Args:
            installment_id: ID da parcela a ser paga
            data_pagamento: Data em que o pagamento foi realizado
            pago_por_user_id: ID do usuário que está registrando o pagamento
            pago_por_nome: Nome do usuário que está registrando
            modality_id: ID da modalidade de pagamento usada (ex: "Dinheiro", "PIX")
            valor_juros: Juros cobrados no pagamento (default: 0)
            valor_multa: Multa cobrada no pagamento (default: 0)
            observacao: Observações sobre o pagamento

        Returns:
            dict: Parcela atualizada e lançamento financeiro criado

        Raises:
            ValueError: Se a parcela não for encontrada ou já estiver paga
        """
        # Buscar a parcela
        installment = self.credit_installment_repository.find_by_id(installment_id)
        if not installment:
            raise ValueError("Parcela não encontrada")

        # Verificar se já está paga
        if installment.status == "pago":
            raise ValueError("Parcela já está paga")

        # Verificar se está cancelada
        if installment.status == "cancelado":
            raise ValueError("Não é possível pagar uma parcela cancelada")

        # Buscar a compra
        credit_purchase = self.credit_purchase_repository.find_by_id(
            installment.credit_purchase_id
        )
        if not credit_purchase:
            raise ValueError("Compra não encontrada")

        # Verificar se a compra está cancelada
        if credit_purchase.status == "cancelado":
            raise ValueError("Não é possível pagar parcela de uma compra cancelada")

        # Buscar a modalidade de pagamento
        modality = self.payment_modality_repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade de pagamento não encontrada")

        # Verificar se a modalidade está ativa
        if not modality.is_active:
            raise ValueError("Modalidade de pagamento está inativa")

        # Atualizar valores de juros e multa na parcela
        installment.valor_juros = valor_juros
        installment.valor_multa = valor_multa

        # Calcular valor total pago
        valor_total_pago = installment.get_valor_total()

        # Criar o lançamento financeiro
        financial_entry = FinancialEntry(
            value=valor_total_pago,
            date=data_pagamento,
            modality_id=modality.id,
            modality_name=modality.name,
            modality_color=modality.color
        )

        # Salvar o lançamento
        created_entry = self.financial_entry_repository.create(financial_entry)

        # Marcar a parcela como paga e vincular ao lançamento
        installment.marcar_como_pago(
            data_pagamento=data_pagamento,
            financial_entry_id=created_entry.id,
            pago_por_user_id=pago_por_user_id,
            pago_por_nome=pago_por_nome,
            valor_juros=valor_juros,
            valor_multa=valor_multa,
            observacao=observacao
        )

        # Salvar a parcela atualizada
        updated_installment = self.credit_installment_repository.update(installment)

        # Verificar se todas as parcelas foram pagas
        self._check_and_complete_purchase(credit_purchase.id)

        return {
            "installment": updated_installment.to_dict(),
            "financial_entry": created_entry.to_dict()
        }

    def _check_and_complete_purchase(self, credit_purchase_id: str) -> None:
        """
        Verifica se todas as parcelas de uma compra foram pagas.
        Se sim, marca a compra como concluída.

        Args:
            credit_purchase_id: ID da compra a verificar
        """
        # Buscar todas as parcelas da compra
        all_installments = self.credit_installment_repository.find_by_credit_purchase(
            credit_purchase_id
        )

        # Verificar se todas estão pagas
        todas_pagas = all(inst.status == "pago" for inst in all_installments)

        if todas_pagas:
            # Buscar e atualizar a compra
            credit_purchase = self.credit_purchase_repository.find_by_id(credit_purchase_id)
            if credit_purchase and credit_purchase.status == "ativo":
                credit_purchase.complete()
                self.credit_purchase_repository.update(credit_purchase)
