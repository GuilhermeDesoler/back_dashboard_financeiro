from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Feature:
    code: str
    name: str
    description: str
    module: str
    is_system: bool = True
    id: Optional[str] = None
    created_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "code": self.code,
            "name": self.name,
            "description": self.description,
            "module": self.module,
            "is_system": self.is_system,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @staticmethod
    def _parse_datetime(value) -> Optional[datetime]:
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        return datetime.fromisoformat(value)
