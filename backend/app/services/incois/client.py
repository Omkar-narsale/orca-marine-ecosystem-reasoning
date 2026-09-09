"""
INCOIS Query-Driven Client & Data Connector.
Orchestrates: Intent -> Location -> Temporal -> Dataset Discovery -> ERDDAP Subsetting -> Normalization -> Aggregation.
Enforces zero hardcoded baseline records. Returns DATA_UNAVAILABLE when live retrieval fails.
"""

import httpx
import time
import asyncio
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from backend.app.services.base import MarineDataConnector
from backend.app.schemas.marine import NormalizedMarineRecord, DataStatusEnum, ProviderDataResponse
from backend.app.schemas.evidence import SourceHealthSchema
from backend.app.core.config import settings
from backend.app.core.logging import log_source_request, logger

from backend.app.services.incois.datasets import VERIFIED_INCOIS_DATASETS, INCOISDatasetMetadata
from backend.app.services.incois.location import resolve_location, build_marine_bbox, get_radius_for_intent, ResolvedLocation, COASTAL_LOCATION_REGISTRY
from backend.app.services.incois.temporal import resolve_time_window, ResolvedTimeWindow
from backend.app.services.incois.discovery import discovery_engine
from backend.app.services.incois.query_builder import query_builder
from backend.app.services.incois.parser import response_parser
from backend.app.services.incois.normalizer import normalizer
from backend.app.services.incois.spatial_aggregator import spatial_aggregator
from backend.app.services.incois.temporal_aggregator import temporal_aggregator
from backend.app.services.incois.cache import incois_cache
from backend.app.services.incois.health import health_inspector

class INCOISConnector(MarineDataConnector):
    def __init__(self):
        super().__init__(
            source_id="INCOIS_OSF",
            name="INCOIS",
            organization="Indian National Centre for Ocean Information Services",
            base_url=settings.INCOIS_ERDDAP_URL
        )
        self.osf_url = settings.INCOIS_OSF_URL
        self.pfz_url = settings.INCOIS_PFZ_URL
        self.erddap_url = settings.INCOIS_ERDDAP_URL
        self.last_error: Optional[str] = None
        self.last_latency_ms: Optional[float] = None

    async def health_check(self) -> SourceHealthSchema:
        return await health_inspector.check_health()

    async def _fetch_with_retry(self, url: str, max_retries: int = 1) -> httpx.Response:
        """Executes HTTP GET with bounded retry."""
        headers = {"User-Agent": "ORCA-Marine-Intelligence/4.0 (SIH-2026-INCOIS-Query)"}
        last_exc = None
        for attempt in range(max_retries + 1):
            try:
                async with httpx.AsyncClient(headers=headers, timeout=settings.HTTP_TIMEOUT_SECONDS, verify=False) as client:
                    res = await client.get(url)
                    if res.status_code in (200, 301, 302):
                        return res
            except Exception as e:
                last_exc = e
                if attempt < max_retries:
                    await asyncio.sleep(0.15 * (2 ** attempt))
        if last_exc:
            raise last_exc
        raise httpx.HTTPError(f"Failed after {max_retries} retries to connect to {url}")

    async def query_marine_telemetry(
        self,
        intent: str = "SEA_CONDITIONS",
        location_query: str = "Maharashtra",
        time_expression: str = "tomorrow morning",
        parameters: Optional[List[str]] = None,
        force_failure: bool = False
    ) -> Dict[str, Any]:
        """
        Main query-driven retrieval pipeline for INCOIS ERDDAP.
        Returns DATA_UNAVAILABLE on failure with zero fabricated numbers.
        """
        if force_failure:
            return {
                "status": DataStatusEnum.DATA_UNAVAILABLE.value,
                "reason": "SIMULATED_FAILURE",
                "location": {"name": location_query},
                "time_window": {"display_label": time_expression},
                "parameters_requested": parameters or [],
                "record_count": 0,
                "nearest_records": [],
                "all_records": [],
                "queries_executed": [],
                "cache_hits": 0,
                "latency_ms": 0.0
            }

        start_t = time.perf_counter()

        # 1. Location Resolution
        location_res: ResolvedLocation = resolve_location(location_query)
        radius_km = get_radius_for_intent(intent)
        bbox = build_marine_bbox(
            latitude=location_res.latitude,
            longitude=location_res.longitude,
            radius_km=radius_km,
            marine_bearing=location_res.marine_bearing
        )

        # 2. Time Window Resolution
        time_window: ResolvedTimeWindow = resolve_time_window(time_expression)

        # 3. Parameter & Dataset Discovery
        needed_params = parameters or discovery_engine.get_data_requirements_for_intent(intent)
        discovered_datasets = discovery_engine.discover_datasets_for_parameters(needed_params)

        all_normalized_records: List[NormalizedMarineRecord] = []
        queries_executed = []
        cache_hits = 0

        # 4. Execute Subsets across Discovered Datasets
        for ds_item in discovered_datasets:
            ds_meta: INCOISDatasetMetadata = ds_item["metadata"]
            vars_to_query: List[str] = ds_item["variables"]

            # Check deterministic cache
            cached = incois_cache.get(
                dataset_id=ds_meta.dataset_id,
                variables=vars_to_query,
                bbox=bbox,
                start_time=time_window.start_utc,
                end_time=time_window.end_utc
            )

            if cached is not None:
                all_normalized_records.extend(cached)
                cache_hits += 1
                log_source_request(
                    source_name="INCOIS",
                    endpoint=ds_meta.dataset_id,
                    operation=f"get_{ds_meta.dataset_id}",
                    cache_hit=True
                )
                continue

            # Construct ERDDAP URL
            if ds_meta.endpoint_type == "griddap":
                query_url = query_builder.build_griddap_query(
                    dataset_meta=ds_meta,
                    variables=vars_to_query,
                    start_time_utc=time_window.start_utc,
                    end_time_utc=time_window.end_utc,
                    min_lat=bbox["min_lat"],
                    max_lat=bbox["max_lat"],
                    min_lon=bbox["min_lon"],
                    max_lon=bbox["max_lon"]
                )
            else:
                query_url = query_builder.build_tabledap_query(
                    dataset_meta=ds_meta,
                    variables=vars_to_query,
                    start_time_utc=time_window.start_utc,
                    min_lat=bbox["min_lat"],
                    max_lat=bbox["max_lat"],
                    min_lon=bbox["min_lon"],
                    max_lon=bbox["max_lon"]
                )

            queries_executed.append({"dataset": ds_meta.dataset_id, "url": query_url})

            # Fetch & Parse
            records_for_dataset: List[NormalizedMarineRecord] = []
            ds_start = time.perf_counter()
            try:
                res = await self._fetch_with_retry(query_url, max_retries=1)
                ds_latency = (time.perf_counter() - ds_start) * 1000.0
                payload = res.json()
                parsed_table = response_parser.parse_json(ds_meta.dataset_id, payload, source_url=query_url)
                records_for_dataset = normalizer.normalize_records(parsed_table.records, ds_meta, source_url=query_url)
                log_source_request(
                    source_name="INCOIS",
                    endpoint=query_url,
                    operation=f"get_{ds_meta.dataset_id}",
                    status_code=res.status_code,
                    record_count=len(records_for_dataset),
                    latency_ms=ds_latency,
                    cache_hit=False
                )
            except Exception as e:
                ds_latency = (time.perf_counter() - ds_start) * 1000.0
                logger.warning(f"[INCOIS] Dataset query failed for {ds_meta.dataset_id}: {e}")
                log_source_request(
                    source_name="INCOIS",
                    endpoint=query_url,
                    operation=f"get_{ds_meta.dataset_id}",
                    status_code=500,
                    record_count=0,
                    latency_ms=ds_latency,
                    cache_hit=False,
                    error=str(e)
                )
                records_for_dataset = []

            if records_for_dataset:
                incois_cache.set(
                    dataset_id=ds_meta.dataset_id,
                    variables=vars_to_query,
                    bbox=bbox,
                    start_time=time_window.start_utc,
                    end_time=time_window.end_utc,
                    records=records_for_dataset
                )
                all_normalized_records.extend(records_for_dataset)

        total_latency = (time.perf_counter() - start_t) * 1000.0
        self.last_latency_ms = total_latency
        if all_normalized_records:
            self.last_successful_retrieval = datetime.now().strftime("%d %b %Y %H:%M IST")

        # 5. Extract Nearest-Point Representative Metrics
        nearest_records = spatial_aggregator.get_nearest_point_records(
            all_normalized_records,
            target_lat=location_res.latitude,
            target_lon=location_res.longitude
        )

        status_str = DataStatusEnum.SUCCESS.value if all_normalized_records else DataStatusEnum.DATA_UNAVAILABLE.value

        return {
            "source": "INCOIS",
            "status": status_str,
            "location": {
                "name": location_res.name,
                "state": location_res.state,
                "coast": location_res.coast,
                "latitude": location_res.latitude,
                "longitude": location_res.longitude,
                "bbox": bbox
            },
            "time_window": {
                "start_utc": time_window.start_utc,
                "end_utc": time_window.end_utc,
                "display_label": time_window.display_label,
                "source_expression": time_window.source_expression
            },
            "parameters_requested": needed_params,
            "record_count": len(all_normalized_records),
            "nearest_records": nearest_records,
            "all_records": all_normalized_records,
            "queries_executed": queries_executed,
            "cache_hits": cache_hits,
            "latency_ms": round(total_latency, 1)
        }

    async def get_data(
        self,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None,
        parameters: Optional[List[str]] = None,
        force_failure: bool = False
    ) -> List[NormalizedMarineRecord]:
        """
        Retrieves live INCOIS records via dynamic location-based query.
        Returns empty list when service is unreachable (ZERO hardcoded baseline records).
        """
        if force_failure:
            raise ConnectionError("Simulated INCOIS connection failure")

        loc_str = "Maharashtra"
        if min_lat is not None and min_lon is not None:
            for name, loc in COASTAL_LOCATION_REGISTRY.items():
                if abs(loc.latitude - min_lat) < 1.0 and abs(loc.longitude - min_lon) < 1.0:
                    loc_str = name
                    break

        try:
            result = await self.query_marine_telemetry(
                intent="SEA_CONDITIONS",
                location_query=loc_str,
                time_expression="tomorrow morning",
                parameters=parameters,
                force_failure=force_failure
            )
            return result.get("all_records", [])
        except Exception as e:
            logger.warning(f"[INCOIS] get_data retrieval error: {e}")
            return []

    async def get_metadata(self) -> Dict[str, Any]:
        return {
            "source_id": self.source_id,
            "name": self.name,
            "organization": self.organization,
            "parameters": [
                "significant_wave_height",
                "wave_period",
                "wave_direction",
                "sea_surface_temperature",
                "surface_current_velocity",
                "chlorophyll_concentration",
                "potential_fishing_zone_advisory"
            ],
            "models": ["Wave Watch III", "ROMS 3D Ocean Model", "OISST Thermal Composite", "OCM-3"],
            "dataset_count": len(VERIFIED_INCOIS_DATASETS),
            "datasets": [ds.dataset_id for ds in VERIFIED_INCOIS_DATASETS.values()],
            "official_url": self.osf_url,
            "erddap_server": self.erddap_url
        }

incois_connector = INCOISConnector()
