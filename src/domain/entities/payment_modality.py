from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PaymentModality:
    name: str
    color: str
    bank_name: str = ""  # Nome do banco (Sicredi, Sicoob, Link Sicredi, etc)
    fee_percentage: float = 0.0  # Taxa percentual (ex: 0.9, 1.1, 1.4)
    rental_fee: float = 0.0  # Aluguel mensal (ex: R$ 56,90)
    is_active: bool = True
    is_credit_plan: bool = False
    allows_anticipation: bool = False
    allows_credit_payment: bool = False
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "bank_name": self.bank_name,
            "fee_percentage": self.fee_percentage,
            "rental_fee": self.rental_fee,
            "is_active": self.is_active,
            "is_credit_plan": self.is_credit_plan,
            "allows_anticipation": self.allows_anticipation,
            "allows_credit_payment": self.allows_credit_payment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now()

    def deactive(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now()
