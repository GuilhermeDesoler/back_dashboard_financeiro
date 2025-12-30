from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class User:
    email: str
    password_hash: str
    name: str
    company_id: str
    role_ids: List[str]
    is_active: bool = True
    is_super_admin: bool = False
    id: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "company_id": self.company_id,
            "role_ids": self.role_ids,
            "is_active": self.is_active,
            "is_super_admin": self.is_super_admin,
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
