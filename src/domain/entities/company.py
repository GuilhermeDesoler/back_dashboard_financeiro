from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Company:
    name: str
    cnpj: str
    phone: str
    plan: str = "basic"
    is_active: bool = True
    settings: Optional[Dict[str, Any]] = None
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {
                "timezone": "America/Sao_Paulo",
                "currency": "BRL"
            }

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "cnpj": self.cnpj,
            "phone": self.phone,
            "plan": self.plan,
            "is_active": self.is_active,
            "settings": self.settings,
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
