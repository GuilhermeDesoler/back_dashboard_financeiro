"""
Implementação MongoDB do repositório de Parcelas do Crediário
"""
from datetime import datetime, timedelta, date
from typing import List, Optional, Dict, Any
from pymongo.database import Database

from src.domain.entities.credit_installment import CreditInstallment
from src.domain.repositories.credit_installment_repository import CreditInstallmentRepository


class MongoCreditInstallmentRepository(CreditInstallmentRepository):
    """Implementação do repositório de parcelas do crediário usando MongoDB"""

    def __init__(self, database: Database):
        """
        Args:
            database: Instância do banco de dados MongoDB (tenant-specific)
        """
        self.collection = database["credit_installments"]

    def create(self, installment: CreditInstallment) -> CreditInstallment:
        """Cria uma nova parcela"""
        installment.validate()
        data = installment.to_dict()
        self.collection.insert_one(data)
        return installment

    def create_many(self, installments: List[CreditInstallment]) -> List[CreditInstallment]:
        """Cria múltiplas parcelas de uma vez"""
        if not installments:
            return []

        for installment in installments:
            installment.validate()

        data_list = [inst.to_dict() for inst in installments]
        self.collection.insert_many(data_list)
        return installments

    def find_by_id(self, installment_id: str) -> Optional[CreditInstallment]:
        """Busca uma parcela pelo ID"""
        data = self.collection.find_one({"id": installment_id})
        if data:
            return CreditInstallment.from_dict(data)
        return None

    def find_by_credit_purchase(
        self,
        credit_purchase_id: str,
        status: Optional[str] = None
    ) -> List[CreditInstallment]:
        """Busca todas as parcelas de uma compra específica"""
        query = {"credit_purchase_id": credit_purchase_id}

        if status:
            query["status"] = status

        cursor = self.collection.find(query).sort("numero_parcela", 1)
        return [CreditInstallment.from_dict(data) for data in cursor]

    def find_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None
    ) -> List[CreditInstallment]:
        """Busca parcelas por intervalo de datas de vencimento"""
        query = {
            "data_vencimento": {
                "$gte": start_date,
                "$lte": end_date
            }
        }

        if status:
            query["status"] = status

        cursor = self.collection.find(query).sort("data_vencimento", 1)
        return [CreditInstallment.from_dict(data) for data in cursor]

    def find_overdue(self) -> List[CreditInstallment]:
        """Busca todas as parcelas atrasadas"""
        hoje = datetime.combine(date.today(), datetime.min.time())

        query = {
            "status": "atrasado",
            "data_pagamento": None,
            "data_vencimento": {"$lt": hoje}
        }

        cursor = self.collection.find(query).sort("data_vencimento", 1)
        return [CreditInstallment.from_dict(data) for data in cursor]

    def find_due_soon(self, days: int = 7) -> List[CreditInstallment]:
        """Busca parcelas que vencem nos próximos N dias"""
        hoje = datetime.combine(date.today(), datetime.min.time())
        data_limite = hoje + timedelta(days=days)

        query = {
            "status": {"$in": ["pendente", "atrasado"]},
            "data_pagamento": None,
            "data_vencimento": {
                "$gte": hoje,
                "$lte": data_limite
            }
        }

        cursor = self.collection.find(query).sort("data_vencimento", 1)
        return [CreditInstallment.from_dict(data) for data in cursor]

    def update(self, installment: CreditInstallment) -> CreditInstallment:
        """Atualiza uma parcela existente"""
        installment.validate()
        installment.updated_at = datetime.utcnow()
        data = installment.to_dict()

        self.collection.update_one(
            {"id": installment.id},
            {"$set": data}
        )
        return installment

    def delete(self, installment_id: str) -> bool:
        """Remove uma parcela"""
        result = self.collection.delete_one({"id": installment_id})
        return result.deleted_count > 0

    def delete_by_credit_purchase(self, credit_purchase_id: str) -> int:
        """Remove todas as parcelas de uma compra"""
        result = self.collection.delete_many({"credit_purchase_id": credit_purchase_id})
        return result.deleted_count

    def get_dashboard_by_date(
        self,
        start_date: datetime,
        end_date: datetime,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtém dados agregados para o dashboard, agrupados por data de vencimento"""
        match_stage = {
            "data_vencimento": {
                "$gte": start_date,
                "$lte": end_date
            }
        }

        if status:
            match_stage["status"] = status

        pipeline = [
            {"$match": match_stage},
            {
                "$sort": {"data_vencimento": 1, "numero_parcela": 1}
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": "%Y-%m-%d",
                            "date": "$data_vencimento"
                        }
                    },
                    "total_dia": {"$sum": "$valor_total"},
                    "quantidade_parcelas": {"$sum": 1},
                    "installments": {"$push": "$$ROOT"}
                }
            },
            {"$sort": {"_id": 1}}
        ]

        results = list(self.collection.aggregate(pipeline))

        # Formatar resultado
        installments_by_date = []
        for item in results:
            installments_by_date.append({
                "data_vencimento": item["_id"],
                "total_dia": item["total_dia"],
                "quantidade_parcelas": item["quantidade_parcelas"],
                "installments": [CreditInstallment.from_dict(inst).to_dict() for inst in item["installments"]]
            })

        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "installments_by_date": installments_by_date
        }

    def get_totals(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obtém totais gerais das parcelas"""
        match_stage = {}

        if start_date or end_date:
            match_stage["data_vencimento"] = {}
            if start_date:
                match_stage["data_vencimento"]["$gte"] = start_date
            if end_date:
                match_stage["data_vencimento"]["$lte"] = end_date

        pipeline = []

        if match_stage:
            pipeline.append({"$match": match_stage})

        pipeline.extend([
            {
                "$group": {
                    "_id": None,
                    "total_parcelas": {"$sum": 1},
                    "total_valor": {"$sum": "$valor_total"},
                    "total_pago": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "pago"]}, "$valor_total", 0]
                        }
                    },
                    "total_pendente": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "pendente"]}, "$valor_total", 0]
                        }
                    },
                    "total_atrasado": {
                        "$sum": {
                            "$cond": [{"$eq": ["$status", "atrasado"]}, "$valor_total", 0]
                        }
                    },
                    "parcelas_pagas": {
                        "$sum": {"$cond": [{"$eq": ["$status", "pago"]}, 1, 0]}
                    },
                    "parcelas_pendentes": {
                        "$sum": {"$cond": [{"$eq": ["$status", "pendente"]}, 1, 0]}
                    },
                    "parcelas_atrasadas": {
                        "$sum": {"$cond": [{"$eq": ["$status", "atrasado"]}, 1, 0]}
                    },
                }
            }
        ])

        result = list(self.collection.aggregate(pipeline))

        if result:
            totals = result[0]
            totals.pop("_id", None)

            # Calcular taxa de inadimplência
            if totals["total_valor"] > 0:
                totals["taxa_inadimplencia"] = round(
                    (totals["total_atrasado"] / totals["total_valor"]) * 100, 2
                )
            else:
                totals["taxa_inadimplencia"] = 0.0

            return totals

        return {
            "total_parcelas": 0,
            "total_valor": 0.0,
            "total_pago": 0.0,
            "total_pendente": 0.0,
            "total_atrasado": 0.0,
            "parcelas_pagas": 0,
            "parcelas_pendentes": 0,
            "parcelas_atrasadas": 0,
            "taxa_inadimplencia": 0.0,
        }

    def update_statuses_batch(self) -> int:
        """Atualiza o status de todas as parcelas pendentes para atrasado quando vencidas"""
        hoje = datetime.combine(date.today(), datetime.min.time())

        result = self.collection.update_many(
            {
                "status": "pendente",
                "data_pagamento": None,
                "data_vencimento": {"$lt": hoje}
            },
            {
                "$set": {
                    "status": "atrasado",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return result.modified_count

    def cancel_all_by_credit_purchase(self, credit_purchase_id: str) -> int:
        """Cancela todas as parcelas pendentes/atrasadas de uma compra"""
        result = self.collection.update_many(
            {
                "credit_purchase_id": credit_purchase_id,
                "status": {"$in": ["pendente", "atrasado"]}
            },
            {
                "$set": {
                    "status": "cancelado",
                    "updated_at": datetime.utcnow()
                }
            }
        )

        return result.modified_count
