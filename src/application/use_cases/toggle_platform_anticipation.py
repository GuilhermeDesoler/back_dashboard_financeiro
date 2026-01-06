from src.domain.entities import PlatformSettings
from src.domain.repositories import PlatformSettingsRepository


class TogglePlatformAnticipation:
    def __init__(self, repository: PlatformSettingsRepository):
        self._repository = repository

    def execute(self) -> PlatformSettings:
        return self._repository.toggle_anticipation()
