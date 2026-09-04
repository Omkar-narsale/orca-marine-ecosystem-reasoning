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
    dataType: Literal["forecast", "observation", "advisory", "warning", "static"]
    timestamp: str
    validFor: str
    retrievedAt: str
    sourceUrl: str
    status: Literal["Connected / Live", "Connected / Synced", "Configured / Auth Required", "Static Baseline", "Degraded / Offline"]
    freshness: str
    lastSuccessfulRetrieval: Optional[str] = None
    recordsAvailable: int = 0

class DataFreshnessSchema(BaseModel):
    parameter: str
    cadence: str
    nature: Literal["Forecast", "Observation", "Advisory", "Warning", "Static"]
    validityTime: str
    provider: str
    freshnessState: str
    retrievedAt: str

class SourceHealthSchema(BaseModel):
    source_id: str
    name: str
    organization: str
    status: str
    endpoint: str
    last_checked: str
    last_successful_retrieval: Optional[str] = None
    response_latency_ms: Optional[float] = None
    is_live: bool
    notes: str

class SystemHealthResponse(BaseModel):
    status: str
    timestamp: str
    total_sources: int
    connected_sources: int
    sources: List[SourceHealthSchema]
