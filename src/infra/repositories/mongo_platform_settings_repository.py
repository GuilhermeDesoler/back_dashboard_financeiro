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
            markup_default=0.0,
            markup_cost=0.0,
            markup_percentage=0.0,
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

    def update_markup_settings(
        self,
        markup_default: Optional[float] = None,
        markup_cost: Optional[float] = None,
        markup_percentage: Optional[float] = None
    ) -> PlatformSettings:
        current_settings = self.get_settings()
        current_settings.update_markup_settings(
            markup_default=markup_default,
            markup_cost=markup_cost,
            markup_percentage=markup_percentage
        )
        return self.update_settings(current_settings)

    def _doc_to_entity(self, doc: dict) -> PlatformSettings:
        return PlatformSettings(
            id=doc["_id"],
            markup_default=doc.get("markup_default", 0.0),
            markup_cost=doc.get("markup_cost", 0.0),
            markup_percentage=doc.get("markup_percentage", 0.0),
            created_at=PlatformSettings._parse_datetime(doc.get("created_at")),
            updated_at=PlatformSettings._parse_datetime(doc.get("updated_at"))
        )
