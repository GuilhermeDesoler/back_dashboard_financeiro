from typing import Optional
from datetime import datetime
from pymongo.collection import Collection

from src.domain.entities import PlatformSettings
from src.domain.repositories import PlatformSettingsRepository


class MongoPlatformSettingsRepository(PlatformSettingsRepository):
    SETTINGS_ID = "platform_settings"

    def __init__(self, collection: Collection):
        self._collection = collection

    def get_settings(self) -> Optional[PlatformSettings]:
        doc = self._collection.find_one({"_id": self.SETTINGS_ID})
        if doc:
            return self._doc_to_entity(doc)

        # Se não existir, criar com valores padrão
        default_settings = PlatformSettings(
            id=self.SETTINGS_ID,
            is_anticipation_enabled=False,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        settings_dict = default_settings.to_dict()
        settings_dict['_id'] = self.SETTINGS_ID
        settings_dict.pop('id')

        self._collection.insert_one(settings_dict)

        return default_settings

    def update_settings(self, settings: PlatformSettings) -> PlatformSettings:
        settings.updated_at = datetime.now()

        settings_dict = settings.to_dict()
        settings_dict.pop('id', None)

        self._collection.update_one(
            {"_id": self.SETTINGS_ID},
            {"$set": settings_dict},
            upsert=True
        )

        settings.id = self.SETTINGS_ID
        return settings

    def toggle_anticipation(self) -> PlatformSettings:
        current_settings = self.get_settings()
        current_settings.toggle_anticipation()
        return self.update_settings(current_settings)

    def _doc_to_entity(self, doc: dict) -> PlatformSettings:
        return PlatformSettings(
            id=doc["_id"],
            is_anticipation_enabled=doc.get("is_anticipation_enabled", False),
            created_at=PlatformSettings._parse_datetime(doc.get("created_at")),
            updated_at=PlatformSettings._parse_datetime(doc.get("updated_at"))
        )
