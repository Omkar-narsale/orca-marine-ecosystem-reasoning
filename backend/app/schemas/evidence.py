from typing import Optional, List, Literal
from pydantic import BaseModel, Field

class EvidenceSourceSchema(BaseModel):
    id: str
    name: str
    shortName: str
    organization: str
    title: str
    parameter: str
    description: str
    type: Literal["Forecast", "Observation", "Advisory", "Geospatial Cadastre"]
    dataType: Literal["forecast", "observation", "advisory", "warning", "static", "cached", "unknown"]
    timestamp: str
    validFor: str
    retrievedAt: str
    sourceUrl: str
    status: str
    freshness: str
    lastSuccessfulRetrieval: Optional[str] = None
    recordsAvailable: int = 0

class DataFreshnessSchema(BaseModel):
    parameter: str
    cadence: str
    nature: str
    validityTime: str
    provider: str
    freshnessState: str
    retrievedAt: str

class SourceHealthSchema(BaseModel):
    source_id: str
    name: str
    organization: str
    status: str  # HEALTHY, DEGRADED, UNAVAILABLE, UNKNOWN, Connected / Live, etc.
    health_state: Optional[str] = None # HEALTHY, DEGRADED, UNAVAILABLE, UNKNOWN
    endpoint: str
    last_checked: str
    last_successful_retrieval: Optional[str] = None
    last_successful_fetch: Optional[str] = None
    response_latency_ms: Optional[float] = None
    latency_ms: Optional[float] = None
    data_freshness: Optional[str] = None
    is_live: bool
    error: Optional[str] = None
    notes: str

class SystemHealthResponse(BaseModel):
    status: str  # healthy, degraded, unavailable
    health_level: Optional[str] = "HEALTHY" # HEALTHY, DEGRADED, UNAVAILABLE
    timestamp: str
    total_sources: int
    connected_sources: int
    sources: List[SourceHealthSchema]

class ReadinessResponse(BaseModel):
    status: str  # READY, DEGRADED, NOT_READY
    ready: bool
    timestamp: str
    dependencies: dict
