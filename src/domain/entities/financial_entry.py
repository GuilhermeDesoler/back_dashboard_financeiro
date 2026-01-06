from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class FinancialEntry:
    value: float
    date: datetime
    modality_id: str
    modality_name: str
    modality_color: str
    type: str = "received"  # "received" ou "receivable" (a haver)
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "value": self.value,
            "date": (
                self.date.isoformat() if isinstance(self.date, datetime) else self.date
            ),
            "modality_id": self.modality_id,
            "modality_name": self.modality_name,
            "modality_color": self.modality_color,
            "type": self.type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "FinancialEntry":
        parsed_date = FinancialEntry._parse_datetime(data["date"])

        if parsed_date is None:
            raise ValueError("Data é obrigatório")

        return FinancialEntry(
            id=data.get("id"),
            value=float(data["value"]),
            date=FinancialEntry._parse_datetime_required(data["date"]),
            modality_id=data["modality_id"],
            modality_name=data["modality_name"],
            modality_color=data.get("modality_color", "#000000"),
            type=data.get("type", "received"),
            created_at=FinancialEntry._parse_datetime(data.get("created_at")),
            updated_at=FinancialEntry._parse_datetime(data.get("updated_at")),
        )

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

    @staticmethod
    def _parse_datetime_required(value) -> datetime:
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            return datetime.fromisoformat(value)
        raise ValueError(f"Data inválida: {value}")

    def format_value(self) -> str:
        return (
            f"R$ {self.value:,.2f}".replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )
