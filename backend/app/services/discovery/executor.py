"""
Query Plan Builder & Parallel Execution Engine.
Converts User Intent -> DataRequirements -> Dataset Discovery -> Source Query Builders -> Parallel asyncio Execution.
"""

import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from backend.app.schemas.query_plan import (
    DataRequirement,
    DatasetMetadata,
    LocationContext,
    TimeContext,
    QueryPlan,
    QueryPlanItem,
    ParameterPriority,
    AuthorityType
)
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.services.discovery.service import discovery_service
from backend.app.services.discovery.adapter_interface import MarineDataSource
from backend.app.services.incois.adapter import incois_adapter
from backend.app.services.mosdac.adapter import mosdac_adapter
from backend.app.services.imd.adapter import imd_adapter
from backend.app.services.incois.location import resolve_location, build_marine_bbox, get_radius_for_intent
from backend.app.services.incois.temporal import resolve_time_window
from backend.app.core.logging import logger, log_source_request
from backend.app.core.tracing import get_current_request_id

# Source Adapter Registry
SOURCE_ADAPTER_MAP: Dict[str, MarineDataSource] = {
    "INCOIS": incois_adapter,
    "MOSDAC": mosdac_adapter,
    "IMD": imd_adapter
}

# Intent to Data Requirements Mapping
INTENT_REQUIREMENT_MATRIX: Dict[str, List[Dict[str, Any]]] = {
    "SEA_CONDITIONS": [
        {"param": "WAVE", "pref": ["INCOIS"], "req": True, "prio": ParameterPriority.CRITICAL},
        {"param": "CURRENT", "pref": ["INCOIS"], "req": True, "prio": ParameterPriority.HIGH},
        {"param": "SST", "pref": ["INCOIS"], "req": False, "prio": ParameterPriority.MEDIUM}
    ],
    "WAVE_CONDITIONS": [
        {"param": "WAVE", "pref": ["INCOIS"], "req": True, "prio": ParameterPriority.CRITICAL}
    ],
    "FISHING_SUITABILITY": [
        {"param": "WAVE", "pref": ["INCOIS"], "req": True, "prio": ParameterPriority.CRITICAL},
        {"param": "CHLOROPHYLL", "pref": ["MOSDAC", "INCOIS"], "req": True, "prio": ParameterPriority.HIGH},
        {"param": "SST", "pref": ["INCOIS", "MOSDAC"], "req": False, "prio": ParameterPriority.MEDIUM},
        {"param": "WIND", "pref": ["IMD"], "req": True, "prio": ParameterPriority.HIGH},
        {"param": "WARNINGS", "pref": ["IMD"], "req": True, "prio": ParameterPriority.CRITICAL},
        {"param": "PFZ", "pref": ["INCOIS"], "req": False, "prio": ParameterPriority.MEDIUM}
    ],
    "MARINE_SAFETY": [
        {"param": "WAVE", "pref": ["INCOIS"], "req": True, "prio": ParameterPriority.CRITICAL},
        {"param": "WIND", "pref": ["IMD"], "req": True, "prio": ParameterPriority.CRITICAL},
        {"param": "WARNINGS", "pref": ["IMD"], "req": True, "prio": ParameterPriority.CRITICAL},
        {"param": "CURRENT", "pref": ["INCOIS"], "req": False, "prio": ParameterPriority.MEDIUM}
    ],
    "CHLOROPHYLL_QUERY": [
        {"param": "CHLOROPHYLL", "pref": ["MOSDAC", "INCOIS"], "req": True, "prio": ParameterPriority.CRITICAL}
    ],
    "SST_QUERY": [
        {"param": "SST", "pref": ["INCOIS", "MOSDAC"], "req": True, "prio": ParameterPriority.CRITICAL}
    ],
    "CURRENT_QUERY": [
        {"param": "CURRENT", "pref": ["INCOIS"], "req": True, "prio": ParameterPriority.CRITICAL}
    ],
    "PRODUCTIVITY_ANALYSIS": [
        {"param": "CHLOROPHYLL", "pref": ["MOSDAC", "INCOIS"], "req": True, "prio": ParameterPriority.CRITICAL},
        {"param": "SST", "pref": ["INCOIS", "MOSDAC"], "req": True, "prio": ParameterPriority.HIGH}
    ]
}

class QueryPlanExecutor:
    """
    Builds structured QueryPlans and executes them asynchronously across independent source adapters.
    """

    def create_query_plan(
        self,
        intent: str,
        location_query: str,
        time_expression: str = "tomorrow morning",
        purpose: str = "GENERAL",
        explicit_parameters: Optional[List[str]] = None
    ) -> QueryPlan:
        """
        Constructs a validated QueryPlan with resolved location, time, and discovered source queries.
        """
        # 1. Resolve Location & Seaward Bounding Box
        res_loc = resolve_location(location_query)
        radius = get_radius_for_intent(intent)
        bbox = build_marine_bbox(res_loc.latitude, res_loc.longitude, radius_km=radius, marine_bearing=res_loc.marine_bearing)

        loc_ctx = LocationContext(
            name=res_loc.name,
            latitude=res_loc.latitude,
            longitude=res_loc.longitude,
            marine_bbox=bbox,
            state=res_loc.state,
            coast=res_loc.coast,
            source="COASTAL_GIS_REGISTRY",
            confidence=1.0
        )

        # 2. Resolve Temporal Window
        res_time = resolve_time_window(time_expression)
        time_ctx = TimeContext(
            start=res_time.start_utc,
            end=res_time.end_utc,
            timezone="Asia/Kolkata",
            original_expression=res_time.source_expression,
            display_label=res_time.display_label
        )

        # 3. Determine Data Requirements from Intent & Parameters
        req_specs = INTENT_REQUIREMENT_MATRIX.get(intent.upper(), INTENT_REQUIREMENT_MATRIX["SEA_CONDITIONS"])
        if explicit_parameters:
            req_specs = [r for r in req_specs if r["param"] in [p.upper() for p in explicit_parameters]]
            if not req_specs:
                # Add explicit parameters directly
                for p in explicit_parameters:
                    req_specs.append({"param": p.upper(), "pref": [], "req": True, "prio": ParameterPriority.HIGH})

        requirements: List[DataRequirement] = []
        for s in req_specs:
            requirements.append(DataRequirement(
                parameter=s["param"],
                source_preference=s["pref"],
                required=s["req"],
                time_range=time_ctx,
                spatial_extent=bbox,
                purpose=purpose,
                priority=s["prio"]
            ))

        # 4. Dataset Discovery & Source Query Building for each Requirement
        planned_items: List[QueryPlanItem] = []
        for req in requirements:
            ds = discovery_service.find_best_dataset(req, loc_ctx, time_ctx)
            if not ds:
                planned_items.append(QueryPlanItem(
                    requirement=req,
                    dataset=None,
                    source="UNKNOWN",
                    query_interface="REST_API",
                    query_payload={},
                    status="UNAVAILABLE",
                    error=f"No verified dataset discovered for parameter {req.parameter}"
                ))
                continue

            adapter = SOURCE_ADAPTER_MAP.get(ds.source)
            if not adapter:
                planned_items.append(QueryPlanItem(
                    requirement=req,
                    dataset=ds,
                    source=ds.source,
                    query_interface=ds.query_interface,
                    query_payload={},
                    status="UNAVAILABLE",
                    error=f"No adapter registered for source {ds.source}"
                ))
                continue

            try:
                query_payload = adapter.build_query(
                    dataset=ds,
                    requirement=req,
                    location=loc_ctx,
                    time_window=time_ctx
                )
                planned_items.append(QueryPlanItem(
                    requirement=req,
                    dataset=ds,
                    source=ds.source,
                    query_interface=ds.query_interface,
                    query_payload=query_payload,
                    status="PLANNED"
                ))
            except Exception as e:
                planned_items.append(QueryPlanItem(
                    requirement=req,
                    dataset=ds,
                    source=ds.source,
                    query_interface=ds.query_interface,
                    query_payload={},
                    status="FAILED",
                    error=str(e)
                ))

        return QueryPlan(
            intent=intent,
            location=loc_ctx,
            time=time_ctx,
            purpose=purpose,
            requirements=requirements,
            items=planned_items,
            created_at=datetime.now(timezone.utc).isoformat()
        )

    async def execute_plan(
        self,
        plan: QueryPlan,
        trace_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes planned queries concurrently across independent sources.
        """
        start_t = time.perf_counter()
        req_trace = trace_id or get_current_request_id() or "ORCA-QUERY-PLAN"

        # Separate items that can be executed
        executable_items = [it for it in plan.items if it.status == "PLANNED" and it.dataset and it.source in SOURCE_ADAPTER_MAP]

        async def _run_item(item: QueryPlanItem):
            adapter = SOURCE_ADAPTER_MAP[item.source]
            item_start = time.perf_counter()
            try:
                item.status = "EXECUTING"
                res = await adapter.execute_query(item.query_payload, trace_id=req_trace)
                records = adapter.normalize(
                    parsed_data=res,
                    dataset=item.dataset,
                    location=plan.location,
                    time_window=plan.time
                )
                item.status = "SUCCESS"
                latency = (time.perf_counter() - item_start) * 1000.0
                return {"item": item, "records": records, "latency_ms": latency, "error": None}
            except Exception as e:
                item.status = "FAILED"
                item.error = str(e)
                latency = (time.perf_counter() - item_start) * 1000.0
                logger.error(f"[{req_trace}] Query execution failed for {item.dataset.dataset_id}: {e}")
                return {"item": item, "records": [], "latency_ms": latency, "error": str(e)}

        # Execute all source queries in parallel
        results = await asyncio.gather(*[_run_item(it) for it in executable_items], return_exceptions=False)

        all_records: List[NormalizedMarineRecord] = []
        sources_queried = set()

        for res in results:
            all_records.extend(res["records"])
            sources_queried.add(res["item"].source)

        total_latency = (time.perf_counter() - start_t) * 1000.0

        # Query Audit Logging
        logger.info(
            f"[{req_trace}] [QUERY_AUDIT] Intent: {plan.intent} | Location: {plan.location.name} | "
            f"Sources: {list(sources_queried)} | Records: {len(all_records)} | Latency: {total_latency:.1f}ms"
        )

        return {
            "status": "SUCCESS" if all_records else "DATA_UNAVAILABLE",
            "plan": plan,
            "records": all_records,
            "sources_queried": list(sources_queried),
            "record_count": len(all_records),
            "latency_ms": round(total_latency, 1)
        }

query_plan_executor = QueryPlanExecutor()
