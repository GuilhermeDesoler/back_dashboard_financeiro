from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PaymentModality:
    name: str
    color: str
    is_active: bool = True
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "is_active": self.is_active,
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
