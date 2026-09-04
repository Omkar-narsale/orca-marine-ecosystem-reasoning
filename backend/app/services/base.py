from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.schemas.evidence import SourceHealthSchema

class MarineDataConnector(ABC):
    """
    Abstract connector interface for all authoritative marine & meteorological sources.
    Ensures normalized output and independent failure isolation.
    """
    def __init__(self, source_id: str, name: str, organization: str, base_url: str):
        self.source_id = source_id
        self.name = name
        self.organization = organization
        self.base_url = base_url
        self.last_checked: Optional[str] = None
        self.last_successful_retrieval: Optional[str] = None

    @abstractmethod
    async def get_data(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        parameters: Optional[List[str]] = None
    ) -> List[NormalizedMarineRecord]:
        """Fetch and normalize marine records from the source."""
        pass

    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """Return source metadata, coverage, and cadence."""
        pass

    @abstractmethod
    async def health_check(self) -> SourceHealthSchema:
        """Perform active HTTP check against the source endpoint and report latency/status."""
        pass
