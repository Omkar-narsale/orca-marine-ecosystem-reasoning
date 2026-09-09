"""
INCOIS Marine Intelligence Package.
Provides query-driven ERDDAP dataset discovery, query builders, location and temporal resolvers, parsers, and normalizers.
"""

from backend.app.services.incois.client import incois_connector, INCOISConnector
from backend.app.services.incois.datasets import VERIFIED_INCOIS_DATASETS, INCOISDatasetMetadata
from backend.app.services.incois.discovery import discovery_engine
from backend.app.services.incois.location import resolve_location, build_marine_bbox, COASTAL_LOCATION_REGISTRY
from backend.app.services.incois.temporal import resolve_time_window
from backend.app.services.incois.query_builder import query_builder, ERDDAPQueryBuilder
from backend.app.services.incois.parser import response_parser, ERDDAPResponseParser
from backend.app.services.incois.normalizer import normalizer, ERDDAPNormalizer
from backend.app.services.incois.cache import incois_cache, INCOISQueryCache
from backend.app.services.incois.health import health_inspector, INCOISHealthInspector
from backend.app.services.incois.spatial_aggregator import spatial_aggregator
from backend.app.services.incois.temporal_aggregator import temporal_aggregator

__all__ = [
    "incois_connector",
    "INCOISConnector",
    "VERIFIED_INCOIS_DATASETS",
    "INCOISDatasetMetadata",
    "discovery_engine",
    "resolve_location",
    "build_marine_bbox",
    "COASTAL_LOCATION_REGISTRY",
    "resolve_time_window",
    "query_builder",
    "ERDDAPQueryBuilder",
    "response_parser",
    "ERDDAPResponseParser",
    "normalizer",
    "ERDDAPNormalizer",
    "incois_cache",
    "INCOISQueryCache",
    "health_inspector",
    "INCOISHealthInspector",
    "spatial_aggregator",
    "temporal_aggregator"
]
