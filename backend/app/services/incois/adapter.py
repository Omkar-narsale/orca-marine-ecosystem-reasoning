"""
INCOIS Marine Data Source Adapter.
Implements the MarineDataSource contract for INCOIS ERDDAP, ROMS, and Wave Watch III products.
"""

from typing import Dict, Any, List, Optional
from backend.app.services.discovery.adapter_interface import MarineDataSource
from backend.app.schemas.query_plan import DataRequirement, DatasetMetadata, LocationContext, TimeContext, AuthorityType
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.schemas.evidence import SourceHealthSchema
from backend.app.services.discovery.registry import VERIFIED_DATASET_REGISTRY
from backend.app.services.incois.query_builder import query_builder
from backend.app.services.incois.client import incois_connector
from backend.app.services.incois.datasets import INCOISDatasetMetadata
from backend.app.core.config import settings

class IncoisAdapter(MarineDataSource):
    def __init__(self):
        super().__init__(
            source_id="INCOIS_OSF",
            name="INCOIS",
            organization="Indian National Centre for Ocean Information Services",
            base_url=settings.INCOIS_ERDDAP_URL
        )

    def discover_datasets(self, requirement: DataRequirement) -> List[DatasetMetadata]:
        param = requirement.parameter.upper()
        results = []
        for ds in VERIFIED_DATASET_REGISTRY.values():
            if ds.source == "INCOIS" and (param in [p.upper() for p in ds.parameters] or param in ("WAVE", "CURRENT", "SST", "PFZ", "SEA_CONDITIONS")):
                results.append(ds)
        return results

    async def get_metadata(self) -> Dict[str, Any]:
        return await incois_connector.get_metadata()

    def build_query(
        self,
        dataset: DatasetMetadata,
        requirement: DataRequirement,
        location: LocationContext,
        time_window: TimeContext
    ) -> Dict[str, Any]:
        # Convert schema DatasetMetadata to INCOIS internal metadata
        incois_ds = INCOISDatasetMetadata(
            dataset_id=dataset.dataset_id,
            title=dataset.name,
            category=dataset.parameters[0] if dataset.parameters else "OCEAN",
            variables=dataset.variables,
            dimensions=dataset.dimensions,
            data_type=dataset.data_type,
            official_url=dataset.official_url
        )

        query_url = query_builder.build_griddap_query(
            dataset_meta=incois_ds,
            variables=dataset.variables,
            start_time_utc=time_window.start,
            end_time_utc=time_window.end,
            min_lat=location.marine_bbox["min_lat"],
            max_lat=location.marine_bbox["max_lat"],
            min_lon=location.marine_bbox["min_lon"],
            max_lon=location.marine_bbox["max_lon"]
        )

        return {
            "dataset_id": dataset.dataset_id,
            "source": "INCOIS",
            "query_url": query_url,
            "variables": dataset.variables,
            "dimensions": dataset.dimensions,
            "bbox": location.marine_bbox,
            "time_start": time_window.start,
            "time_end": time_window.end,
            "location_name": location.name,
            "time_expression": time_window.original_expression
        }

    async def execute_query(
        self,
        query_payload: Dict[str, Any],
        trace_id: Optional[str] = None
    ) -> Any:
        return await incois_connector.query_marine_telemetry(
            intent="SEA_CONDITIONS",
            location_query=query_payload.get("location_name", "Nagapattinam"),
            time_expression=query_payload.get("time_expression", "tomorrow morning"),
            parameters=query_payload.get("variables")
        )

    def parse_response(
        self,
        dataset: DatasetMetadata,
        raw_response: Any,
        query_payload: Dict[str, Any]
    ) -> Any:
        return raw_response

    def normalize(
        self,
        parsed_data: Any,
        dataset: DatasetMetadata,
        location: LocationContext,
        time_window: TimeContext
    ) -> List[NormalizedMarineRecord]:
        if isinstance(parsed_data, dict) and "all_records" in parsed_data:
            return parsed_data["all_records"]
        return []

    async def health_check(self) -> SourceHealthSchema:
        return await incois_connector.health_check()

incois_adapter = IncoisAdapter()
