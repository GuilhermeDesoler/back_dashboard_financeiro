from datetime import datetime, timedelta
from typing import List, Optional
from calendar import monthrange
from src.domain.entities import FinancialEntry, Installment
from src.domain.repositories import FinancialEntryRepository, InstallmentRepository
from src.domain.repositories import PaymentModalityRepository


class CreateFinancialEntry:
    def __init__(
        self,
        entry_repository: FinancialEntryRepository,
        modality_repository: PaymentModalityRepository,
        installment_repository: InstallmentRepository
    ):
        self._entry_repository = entry_repository
        self._modality_repository = modality_repository
        self._installment_repository = installment_repository

    def execute(
        self,
        value: float,
        date: datetime,
        modality_id: str,
        installments_count: Optional[int] = None,
        start_date: Optional[datetime] = None,
        is_credit_payment: bool = False
    ) -> dict:
        if value <= 0:
            raise ValueError("Valor deve ser maior que zero")

        modality = self._modality_repository.find_by_id(modality_id)
        if not modality:
            raise ValueError("Modalidade de pagamento não encontrada")

        if not modality.is_active:
            raise ValueError("Modalidade de pagamento está inativa")

        # Se é crediário, parcelas são obrigatórias
        if modality.is_credit_plan:
            if not installments_count or installments_count < 1:
                raise ValueError("Número de parcelas é obrigatório para modalidade de crediário")
            if not start_date:
                raise ValueError("Data de início é obrigatória para modalidade de crediário")

        # Valida se a modalidade permite pagamento de crediário quando usuário marca como tal
        if is_credit_payment and not modality.allows_credit_payment:
            raise ValueError("Esta modalidade não permite pagamento de crediário")

        # Define o tipo baseado na escolha do usuário
        entry_type = "receivable" if is_credit_payment else "received"

        entry = FinancialEntry(
            value=value,
            date=date,
            modality_id=modality_id,
            modality_name=modality.name,
            modality_color=modality.color,
            type=entry_type
        )

        created_entry = self._entry_repository.create(entry)

        # Criar parcelas se for crediário
        created_installments = []
        if modality.is_credit_plan and installments_count:
            created_installments = self._create_installments(
                created_entry.id,
                value,
                installments_count,
                start_date
            )

        return {
            "entry": created_entry,
            "installments": created_installments
        }

    def _create_installments(
        self,
        entry_id: str,
        total_value: float,
        installments_count: int,
        start_date: datetime
    ) -> List[Installment]:
        installment_value = total_value / installments_count
        installments = []

        # Dia de vencimento padrão (da primeira parcela)
        target_day = start_date.day

        for i in range(installments_count):
            # Calcula o mês e ano da parcela
            month = start_date.month + i
            year = start_date.year

            # Ajusta ano se mês ultrapassar 12
            while month > 12:
                month -= 12
                year += 1

            # Descobre quantos dias tem o mês
            last_day_of_month = monthrange(year, month)[1]

            # Se o dia alvo não existir no mês, usa o último dia do mês
            day = min(target_day, last_day_of_month)

            # Cria a data de vencimento
            due_date = datetime(year, month, day, start_date.hour, start_date.minute, start_date.second)

            installment = Installment(
                financial_entry_id=entry_id,
                installment_number=i + 1,
                total_installments=installments_count,
                amount=installment_value,
                due_date=due_date,
                is_paid=False
            )

            created = self._installment_repository.create(installment)
            installments.append(created)

        return installments
