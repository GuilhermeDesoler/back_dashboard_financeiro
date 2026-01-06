from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Literal


@dataclass
class Account:
    """
    Entidade que representa uma conta (boleto, pagamento ou investimento)
    """
    value: float
    date: datetime
    description: str
    type: Literal["boleto", "payment", "investment"]
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        """Helper para converter string ISO para datetime"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace('Z', '+00:00'))
        return None

    def to_dict(self) -> dict:
        """Converte a entidade para dicionário"""
        return {
            "id": self.id,
            "value": self.value,
            "date": self.date.isoformat() if self.date else None,
            "description": self.description,
            "type": self.type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        """Cria uma entidade a partir de um dicionário"""
        return cls(
            id=data.get("id") or data.get("_id"),
            value=data.get("value"),
            date=cls._parse_datetime(data.get("date")),
            description=data.get("description"),
            type=data.get("type"),
            created_at=cls._parse_datetime(data.get("created_at")),
            updated_at=cls._parse_datetime(data.get("updated_at")),
        )
