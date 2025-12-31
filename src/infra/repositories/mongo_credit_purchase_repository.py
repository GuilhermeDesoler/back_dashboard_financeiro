"""
Implementação MongoDB do repositório de Compras no Crediário
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pymongo.database import Database

from src.domain.entities.credit_purchase import CreditPurchase
from src.domain.repositories.credit_purchase_repository import CreditPurchaseRepository


class MongoCreditPurchaseRepository(CreditPurchaseRepository):
    """Implementação do repositório de compras no crediário usando MongoDB"""

    def __init__(self, database: Database):
        """
        Args:
            database: Instância do banco de dados MongoDB (tenant-specific)
        """
        self.collection = database["credit_purchases"]

    def create(self, credit_purchase: CreditPurchase) -> CreditPurchase:
        """Cria uma nova compra no crediário"""
        credit_purchase.validate()
        data = credit_purchase.to_dict()
        self.collection.insert_one(data)
        return credit_purchase

    def find_by_id(self, credit_purchase_id: str) -> Optional[CreditPurchase]:
        """Busca uma compra pelo ID"""
        data = self.collection.find_one({"id": credit_purchase_id})
        if data:
            return CreditPurchase.from_dict(data)
        return None

    def find_all(
        self,
        status: Optional[str] = None,
        pagante_nome: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[CreditPurchase]:
        """Lista todas as compras com filtros opcionais"""
        query = {}

        if status:
            query["status"] = status

        if pagante_nome:
            # Busca case-insensitive e parcial
            query["pagante_nome"] = {"$regex": pagante_nome, "$options": "i"}

        cursor = self.collection.find(query).sort("created_at", -1).skip(skip).limit(limit)
        return [CreditPurchase.from_dict(data) for data in cursor]

    def count(
        self,
        status: Optional[str] = None,
        pagante_nome: Optional[str] = None
    ) -> int:
        """Conta o total de compras com filtros opcionais"""
        query = {}

        if status:
            query["status"] = status

        if pagante_nome:
            query["pagante_nome"] = {"$regex": pagante_nome, "$options": "i"}

        return self.collection.count_documents(query)

    def update(self, credit_purchase: CreditPurchase) -> CreditPurchase:
        """Atualiza uma compra existente"""
        credit_purchase.validate()
        credit_purchase.updated_at = datetime.utcnow()
        data = credit_purchase.to_dict()

        self.collection.update_one(
            {"id": credit_purchase.id},
            {"$set": data}
        )
        return credit_purchase

    def delete(self, credit_purchase_id: str) -> bool:
        """Remove uma compra"""
        result = self.collection.delete_one({"id": credit_purchase_id})
        return result.deleted_count > 0

    def get_statistics(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obtém estatísticas gerais das compras no crediário"""
        match_stage = {}

        if start_date or end_date:
            match_stage["created_at"] = {}
            if start_date:
                match_stage["created_at"]["$gte"] = start_date
            if end_date:
                match_stage["created_at"]["$lte"] = end_date

        pipeline = []

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {
                "$group": {
                    "_id": None,
                    "total_compras": {"$sum": 1},
                    "valor_total": {"$sum": "$valor_total"},
                    "total_ativo": {
                        "$sum": {"$cond": [{"$eq": ["$status", "ativo"]}, 1, 0]}
                    },
                    "total_cancelado": {
                        "$sum": {"$cond": [{"$eq": ["$status", "cancelado"]}, 1, 0]}
                    },
                    "total_concluido": {
                        "$sum": {"$cond": [{"$eq": ["$status", "concluido"]}, 1, 0]}
                    },
                }
            }
        ])

        result = list(self.collection.aggregate(pipeline))

        if result:
            stats = result[0]
            stats.pop("_id", None)
            return stats

        return {
            "total_compras": 0,
            "valor_total": 0.0,
            "total_ativo": 0,
            "total_cancelado": 0,
            "total_concluido": 0,
        }

    def find_by_pagante(self, pagante_nome: str) -> List[CreditPurchase]:
        """Busca todas as compras de um pagante específico"""
        cursor = self.collection.find(
            {"pagante_nome": {"$regex": pagante_nome, "$options": "i"}}
        ).sort("created_at", -1)

        return [CreditPurchase.from_dict(data) for data in cursor]
