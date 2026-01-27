from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class PlatformSettings:
    # Markup settings
    markup_default: float = 0.0  # M - Markup padrão
    markup_cost: float = 0.0  # C - Constante de custo adicional
    markup_percentage: float = 0.0  # Percentual de aumento (ex: 0.05 = 5%)
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "markup_default": self.markup_default,
            "markup_cost": self.markup_cost,
            "markup_percentage": self.markup_percentage,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @staticmethod
    def from_dict(data: dict) -> "PlatformSettings":
        return PlatformSettings(
            id=data.get("id"),
            markup_default=data.get("markup_default", 0.0),
            markup_cost=data.get("markup_cost", 0.0),
            markup_percentage=data.get("markup_percentage", 0.0),
            created_at=PlatformSettings._parse_datetime(data.get("created_at")),
            updated_at=PlatformSettings._parse_datetime(data.get("updated_at")),
        )

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)

    def update_markup_settings(
        self,
        markup_default: Optional[float] = None,
        markup_cost: Optional[float] = None,
        markup_percentage: Optional[float] = None
    ) -> None:
        if markup_default is not None:
            self.markup_default = markup_default
        if markup_cost is not None:
            self.markup_cost = markup_cost
        if markup_percentage is not None:
            self.markup_percentage = markup_percentage
        self.updated_at = datetime.now()
