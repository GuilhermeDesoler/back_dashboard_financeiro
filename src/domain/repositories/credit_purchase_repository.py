"""
Interface do repositório de Compras no Crediário
"""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any

from src.domain.entities.credit_purchase import CreditPurchase


class CreditPurchaseRepository(ABC):
    """Interface para o repositório de compras no crediário"""

    @abstractmethod
    def create(self, credit_purchase: CreditPurchase) -> CreditPurchase:
        """
        Cria uma nova compra no crediário.

        Args:
            credit_purchase: Entidade da compra a ser criada

        Returns:
            CreditPurchase: Compra criada
        """
        pass

    @abstractmethod
    def find_by_id(self, credit_purchase_id: str) -> Optional[CreditPurchase]:
        """
        Busca uma compra pelo ID.

        Args:
            credit_purchase_id: ID da compra

        Returns:
            CreditPurchase ou None se não encontrado
        """
        pass

    @abstractmethod
    def find_all(
        self,
        status: Optional[str] = None,
        pagante_nome: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CreditPurchase]:
        """
        Lista todas as compras com filtros opcionais.

        Args:
            status: Filtrar por status (ativo, cancelado, concluido)
            pagante_nome: Filtrar por nome do pagante (busca parcial)
            skip: Número de registros a pular (paginação)
            limit: Limite de registros a retornar

        Returns:
            Lista de compras
        """
        pass

    @abstractmethod
    def count(
        self,
        status: Optional[str] = None,
        pagante_nome: Optional[str] = None
    ) -> int:
        """
        Conta o total de compras com filtros opcionais.

        Args:
            status: Filtrar por status
            pagante_nome: Filtrar por nome do pagante

        Returns:
            Total de compras
        """
        pass

    @abstractmethod
    def update(self, credit_purchase: CreditPurchase) -> CreditPurchase:
        """
        Atualiza uma compra existente.

        Args:
            credit_purchase: Entidade com os dados atualizados

        Returns:
            Compra atualizada
        """
        pass

    @abstractmethod
    def delete(self, credit_purchase_id: str) -> bool:
        """
        Remove uma compra.

        Args:
            credit_purchase_id: ID da compra a ser removida

        Returns:
            True se removido com sucesso
        """
        pass

    @abstractmethod
    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Obtém estatísticas gerais das compras no crediário.

        Args:
            start_date: Data inicial para filtro
            end_date: Data final para filtro

        Returns:
            Dicionário com estatísticas (total_compras, valor_total, etc.)
        """
        pass

    @abstractmethod
    def find_by_pagante(self, pagante_nome: str) -> List[CreditPurchase]:
        """
        Busca todas as compras de um pagante específico.

        Args:
            pagante_nome: Nome do pagante

        Returns:
            Lista de compras do pagante
        """
        pass
