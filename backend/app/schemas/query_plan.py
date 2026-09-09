"""
Unified Query Planning & Data Requirement Schemas.
Enforces deterministic mapping between User Intent -> Data Requirements -> Dataset Discovery -> Source Query Builders.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field
from enum import Enum

class AuthorityType(str, Enum):
    OFFICIAL_WARNING = "OFFICIAL_WARNING"
    OFFICIAL_ADVISORY = "OFFICIAL_ADVISORY"
    OFFICIAL_FORECAST = "OFFICIAL_FORECAST"
    OFFICIAL_OBSERVATION = "OFFICIAL_OBSERVATION"
    ORCA_DERIVED = "ORCA_DERIVED"
    CACHED = "CACHED"
    UNKNOWN = "UNKNOWN"

class ParameterPriority(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

class LocationContext(BaseModel):
    name: str = Field(..., description="Canonical or identified coastal location name")
    latitude: float = Field(..., description="Center latitude in decimal degrees")
    longitude: float = Field(..., description="Center longitude in decimal degrees")
    marine_bbox: Dict[str, float] = Field(
        ...,
        description="Seaward-oriented marine bounding box: {min_lat, max_lat, min_lon, max_lon}"
    )
    state: Optional[str] = Field("India Coastline", description="State or maritime jurisdiction")
    coast: Optional[str] = Field("General Coast", description="Coast orientation (West Coast, East Coast, etc.)")
    source: str = Field("COASTAL_GIS_REGISTRY", description="Resolution source")
    confidence: float = Field(1.0, description="Geocoding confidence score")

class TimeContext(BaseModel):
    start: str = Field(..., description="Start timestamp in ISO-8601 UTC")
    end: str = Field(..., description="End timestamp in ISO-8601 UTC")
    timezone: str = Field("Asia/Kolkata", description="Local timezone identifier")
    original_expression: str = Field("now", description="Original natural language expression")
    display_label: str = Field("Current", description="User-friendly display representation")

class DataRequirement(BaseModel):
    parameter: str = Field(..., description="Standardized parameter: WAVE, SST, CURRENT, CHLOROPHYLL, WIND, WARNINGS, RESTRICTIONS")
    source_preference: List[str] = Field(default_factory=list, description="Ordered source preference (e.g. ['MOSDAC', 'INCOIS'])")
    required: bool = Field(True, description="Whether this parameter is mandatory for the decision")
    time_range: Optional[TimeContext] = None
    spatial_extent: Optional[Dict[str, float]] = None
    resolution: Optional[str] = Field(None, description="Preferred spatial/temporal resolution")
    purpose: str = Field("GENERAL_ASSESSMENT", description="Operational purpose (FISHING_SUITABILITY, MARINE_SAFETY, etc.)")
    priority: ParameterPriority = Field(ParameterPriority.HIGH, description="Priority level for retrieval")

class DatasetMetadata(BaseModel):
    dataset_id: str = Field(..., description="Official verified dataset identifier")
    source: str = Field(..., description="Official source organization: INCOIS, MOSDAC, IMD")
    name: str = Field(..., description="Human-readable title")
    parameters: List[str] = Field(..., description="Standardized parameters supported by this dataset")
    variables: List[str] = Field(..., description="Actual scientific variable names in the provider schema")
    dimensions: List[str] = Field(default_factory=lambda: ["time", "latitude", "longitude"], description="Dimension axis names in exact order")
    data_type: str = Field("FORECAST", description="Scientific nature: FORECAST, OBSERVATION, ANALYSIS, ADVISORY")
    temporal_resolution: str = Field("3-hourly", description="Temporal step/cadence")
    spatial_resolution: str = Field("0.1 degree", description="Spatial grid resolution")
    coverage: Dict[str, Any] = Field(default_factory=dict, description="Geographical coverage bounding box and bounds")
    query_interface: Literal["ERDDAP", "MOSDAC_DOWNLOAD_API", "IMD_BULLETIN_API", "REST_API"] = Field("ERDDAP")
    verified: bool = Field(True, description="Strictly verified against authoritative provider catalog")
    official_url: str = Field(..., description="Official provider catalog URL")
    description: Optional[str] = None

class QueryPlanItem(BaseModel):
    requirement: DataRequirement
    dataset: Optional[DatasetMetadata] = None
    source: str
    query_interface: str
    query_payload: Dict[str, Any] = Field(default_factory=dict, description="Source-specific query parameters or URL")
    status: Literal["PLANNED", "EXECUTING", "SUCCESS", "FAILED", "CACHED", "UNAVAILABLE"] = "PLANNED"
    error: Optional[str] = None

class QueryPlan(BaseModel):
    intent: str
    location: LocationContext
    time: TimeContext
    purpose: str = "GENERAL"
    requirements: List[DataRequirement] = Field(default_factory=list)
    items: List[QueryPlanItem] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: "")
