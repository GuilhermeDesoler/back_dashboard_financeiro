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
    def toggle_anticipation(self) -> PlatformSettings:
        pass
