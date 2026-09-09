"""
Marine Data Source Adapter Interface.
Defines the standard contract for all authoritative marine & meteorological source adapters.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from backend.app.schemas.query_plan import DataRequirement, DatasetMetadata, LocationContext, TimeContext
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.schemas.evidence import SourceHealthSchema

class MarineDataSource(ABC):
    """
    Abstract Marine Data Source Adapter.
    Enforces distinct dataset discovery, source-specific query construction, 
    isolated network execution, and standardized normalization.
    """
    def __init__(self, source_id: str, name: str, organization: str, base_url: str):
        self.source_id = source_id
        self.name = name
        self.organization = organization
        self.base_url = base_url
        self.last_checked: Optional[str] = None
        self.last_successful_retrieval: Optional[str] = None

    @abstractmethod
    def discover_datasets(self, requirement: DataRequirement) -> List[DatasetMetadata]:
        """Finds verified datasets provided by this source compatible with the data requirement."""
        pass

    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """Returns provider catalog metadata, cadences, and coverage bounds."""
        pass

    @abstractmethod
    def build_query(
        self,
        dataset: DatasetMetadata,
        requirement: DataRequirement,
        location: LocationContext,
        time_window: TimeContext
    ) -> Dict[str, Any]:
        """Builds validated, source-specific query parameters or URL."""
        pass

    @abstractmethod
    async def execute_query(
        self,
        query_payload: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> Any:
        """Executes source-specific HTTP request with exponential backoff and timeouts."""
        pass

    @abstractmethod
    def parse_response(
        self,
        dataset: DatasetMetadata,
        raw_response: Any,
        query_payload: Dict[str, Any]
    ) -> Any:
        """Parses raw provider response format (JSON table, XML/bulletin, geojson)."""
        pass

    @abstractmethod
    def normalize(
        self,
        parsed_data: Any,
        dataset: DatasetMetadata,
        location: LocationContext,
        time_window: TimeContext
    ) -> List[NormalizedMarineRecord]:
        """Normalizes parsed response into standard ORCA NormalizedMarineRecord schema."""
        pass

    @abstractmethod
    async def health_check(self) -> SourceHealthSchema:
        """Performs active diagnostic health check against provider endpoint."""
        pass
