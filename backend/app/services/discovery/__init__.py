"""
Discovery Service Package Exports.
"""

from backend.app.schemas.query_plan import (
    DataRequirement,
    DatasetMetadata,
    LocationContext,
    TimeContext,
    QueryPlan,
    QueryPlanItem,
    AuthorityType,
    ParameterPriority
)
from backend.app.services.discovery.registry import (
    VERIFIED_DATASET_REGISTRY,
    get_verified_dataset,
    list_all_verified_datasets
)
from backend.app.services.discovery.service import discovery_service, DatasetDiscoveryService
from backend.app.services.discovery.adapter_interface import MarineDataSource
from backend.app.services.discovery.executor import query_plan_executor, QueryPlanExecutor

__all__ = [
    "DataRequirement",
    "DatasetMetadata",
    "LocationContext",
    "TimeContext",
    "QueryPlan",
    "QueryPlanItem",
    "AuthorityType",
    "ParameterPriority",
    "VERIFIED_DATASET_REGISTRY",
    "get_verified_dataset",
    "list_all_verified_datasets",
    "discovery_service",
    "DatasetDiscoveryService",
    "MarineDataSource",
    "query_plan_executor",
    "QueryPlanExecutor"
]
