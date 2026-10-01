from abc import ABC, abstractmethod
from typing import List, Callable, Optional
from src.models import GeoBoundingBox, Lead

class BusinessDataProvider(ABC):
    """
    Abstract interface for pluggable business lead data providers.
    Supports OpenStreetMap (free default), Google Places (optional), and custom providers.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider identifier."""
        pass

    @property
    @abstractmethod
    def is_free(self) -> bool:
        """Whether this provider requires paid API credentials."""
        pass

    @abstractmethod
    def search(
        self,
        bbox: GeoBoundingBox,
        category: str,
        keyword: Optional[str] = None,
        max_results: int = 50,
        progress_callback: Optional[Callable[[int, str], None]] = None
    ) -> List[Lead]:
        """
        Executes business search within geographic bounding box.
        Returns a list of raw or semi-normalized Lead objects.
        """
        pass
