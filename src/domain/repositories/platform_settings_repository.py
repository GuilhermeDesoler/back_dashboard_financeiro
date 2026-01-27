from abc import ABC, abstractmethod
from typing import Optional
from src.domain.entities import PlatformSettings


class PlatformSettingsRepository(ABC):
    @abstractmethod
    def get_settings(self) -> Optional[PlatformSettings]:
        pass

    @abstractmethod
    def update_settings(self, settings: PlatformSettings) -> PlatformSettings:
        pass

    @abstractmethod
    def update_markup_settings(
        self,
        markup_default: Optional[float] = None,
        markup_cost: Optional[float] = None,
        markup_percentage: Optional[float] = None
    ) -> PlatformSettings:
        pass
