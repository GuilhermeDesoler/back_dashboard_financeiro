from datetime import datetime
from typing import List, Dict, Any
from collections import defaultdict
from src.domain.repositories import InstallmentRepository, FinancialEntryRepository


class GetDailyCreditSummary:
    def __init__(
        self,
        installment_repository: InstallmentRepository,
        financial_entry_repository: FinancialEntryRepository
    ):
        self._installment_repository = installment_repository
        self._financial_entry_repository = financial_entry_repository

    def execute(
        self,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[Dict[str, Any]]:
        """
        Retorna um resumo diário do crediário com:
        - total_receivable: soma das parcelas a receber (não pagas) naquele dia
        - total_received: soma dos pagamentos de crediário recebidos naquele dia
        - difference: diferença entre recebido e a receber

        Args:
            start_date: Data inicial do período (opcional)
            end_date: Data final do período (opcional)

        Returns:
            Lista de dicionários com resumo por data
        """
        # Buscar todas as parcelas
        all_installments = self._installment_repository.find_all()

        # Buscar todos os lançamentos que são pagamentos de crediário
        if start_date and end_date:
            all_entries = self._financial_entry_repository.find_by_date_range(
                start_date, end_date
            )
        else:
            all_entries = self._financial_entry_repository.find_all()

        # Filtrar apenas lançamentos que são pagamentos de crediário
        credit_payments = [
            entry for entry in all_entries
            if entry.type == "receivable"
        ]

        # Agrupar dados por data
        daily_summary = defaultdict(lambda: {
            "date": None,
            "total_receivable": 0.0,
            "total_received": 0.0,
            "difference": 0.0
        })

        # Processar parcelas a receber (não pagas)
        for installment in all_installments:
            # Aplicar filtro de datas se fornecido
            if start_date and installment.due_date < start_date:
                continue
            if end_date and installment.due_date > end_date:
                continue

            date_key = installment.due_date.strftime("%Y-%m-%d")

            if not installment.is_paid:
                daily_summary[date_key]["total_receivable"] += installment.amount

            if daily_summary[date_key]["date"] is None:
                daily_summary[date_key]["date"] = installment.due_date.strftime("%Y-%m-%d")

        # Processar pagamentos recebidos de crediário
        for entry in credit_payments:
            date_key = entry.date.strftime("%Y-%m-%d")

            daily_summary[date_key]["total_received"] += entry.value

            if daily_summary[date_key]["date"] is None:
                daily_summary[date_key]["date"] = entry.date.strftime("%Y-%m-%d")

        # Calcular diferença e converter para lista
        result = []
        for date_key in sorted(daily_summary.keys(), reverse=True):
            summary = daily_summary[date_key]
            summary["difference"] = summary["total_received"] - summary["total_receivable"]
            result.append(summary)

        return result
