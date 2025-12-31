"""
Interface do repositório de Parcelas do Crediário
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.domain.entities.credit_installment import CreditInstallment


class CreditInstallmentRepository(ABC):
    """Interface para o repositório de parcelas do crediário"""

    @abstractmethod
    def create(self, installment: CreditInstallment) -> CreditInstallment:
        """
        Cria uma nova parcela.

        Args:
            installment: Entidade da parcela a ser criada

        Returns:
            Parcela criada
        """
        pass

    @abstractmethod
    def create_many(self, installments: List[CreditInstallment]) -> List[CreditInstallment]:
        """
        Cria múltiplas parcelas de uma vez (usado na criação da compra).

        Args:
            installments: Lista de parcelas a serem criadas

        Returns:
            Lista de parcelas criadas
        """
        pass

    @abstractmethod
    def find_by_id(self, installment_id: str) -> Optional[CreditInstallment]:
        """
        Busca uma parcela pelo ID.

        Args:
            installment_id: ID da parcela

        Returns:
            Parcela ou None se não encontrada
        """
        pass

    @abstractmethod
    def find_by_credit_purchase(
        self,
        credit_purchase_id: str,
        status: Optional[str] = None
    ) -> List[CreditInstallment]:
        """
        Busca todas as parcelas de uma compra específica.

        Args:
            credit_purchase_id: ID da compra
            status: Filtrar por status (opcional)

        Returns:
            Lista de parcelas da compra
        """
        pass

    @abstractmethod
    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None
    ) -> List[CreditInstallment]:
        """
        Busca parcelas por intervalo de datas de vencimento.

        Args:
            start_date: Data inicial
            end_date: Data final
            status: Filtrar por status (opcional)

        Returns:
            Lista de parcelas no período
        """
        pass

    @abstractmethod
    def find_overdue(self) -> List[CreditInstallment]:
        """
        Busca todas as parcelas atrasadas.

        Returns:
            Lista de parcelas atrasadas
        """
        pass

    @abstractmethod
    def find_due_soon(self, days: int = 7) -> List[CreditInstallment]:
        """
        Busca parcelas que vencem nos próximos N dias.

        Args:
            days: Quantidade de dias para considerar

        Returns:
            Lista de parcelas que vencem em breve
        """
        pass

    @abstractmethod
    def update(self, installment: CreditInstallment) -> CreditInstallment:
        """
        Atualiza uma parcela existente.

        Args:
            installment: Entidade com os dados atualizados

        Returns:
            Parcela atualizada
        """
        pass

    @abstractmethod
    def delete(self, installment_id: str) -> bool:
        """
        Remove uma parcela.

        Args:
            installment_id: ID da parcela a ser removida

        Returns:
            True se removido com sucesso
        """
        pass

    @abstractmethod
    def delete_by_credit_purchase(self, credit_purchase_id: str) -> int:
        """
        Remove todas as parcelas de uma compra.

        Args:
            credit_purchase_id: ID da compra

        Returns:
            Quantidade de parcelas removidas
        """
        pass

    @abstractmethod
    def get_dashboard_by_date(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Obtém dados agregados para o dashboard, agrupados por data de vencimento.

        Args:
            start_date: Data inicial
            end_date: Data final
            status: Filtrar por status (opcional)

        Returns:
            Dicionário com dados agregados por data
        """
        pass

    @abstractmethod
    def get_totals(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtém totais gerais das parcelas (a receber, recebido, atrasado, etc.).

        Args:
            start_date: Data inicial (opcional)
            end_date: Data final (opcional)

        Returns:
            Dicionário com totais
        """
        pass

    @abstractmethod
    def update_statuses_batch(self) -> int:
        """
        Atualiza o status de todas as parcelas pendentes para atrasado
        quando necessário (job automático).

        Returns:
            Quantidade de parcelas atualizadas
        """
        pass

    @abstractmethod
    def cancel_all_by_credit_purchase(self, credit_purchase_id: str) -> int:
        """
        Cancela todas as parcelas pendentes/atrasadas de uma compra.

        Args:
            credit_purchase_id: ID da compra

        Returns:
            Quantidade de parcelas canceladas
        """
        pass
