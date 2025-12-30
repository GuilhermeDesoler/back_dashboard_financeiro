from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.entities import Feature


class FeatureRepository(ABC):
    @abstractmethod
    def create(self, feature: Feature) -> Feature:
        pass

    @abstractmethod
    def find_by_id(self, feature_id: str) -> Optional[Feature]:
        pass

    @abstractmethod
    def find_by_code(self, code: str) -> Optional[Feature]:
        pass

    @abstractmethod
    def find_by_module(self, module: str) -> List[Feature]:
        pass

    @abstractmethod
    def find_all(self) -> List[Feature]:
        pass

    @abstractmethod
    def find_system_features(self) -> List[Feature]:
        pass

    @abstractmethod
    def delete(self, feature_id: str) -> bool:
        pass
