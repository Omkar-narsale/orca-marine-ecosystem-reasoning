from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime

DataTypeLiteral = Literal["forecast", "observation", "advisory", "warning", "static"]

class NormalizedMarineRecord(BaseModel):
    source: str = Field(..., description="Authoritative organization (INCOIS, IMD, MOSDAC, GIS)")
    source_id: str = Field(..., description="Unique source registry ID (INCOIS_OSF, IMD_MARINE, etc.)")
    parameter: str = Field(..., description="Normalized parameter key (e.g. significant_wave_height, surface_wind)")
    value: Any = Field(..., description="Numeric value or structured string")
    unit: str = Field(default="", description="Measurement unit (m, kt, °C, mg/m³)")
    latitude: Optional[float] = Field(default=None, description="Spatial latitude")
    longitude: Optional[float] = Field(default=None, description="Spatial longitude")
    timestamp: str = Field(..., description="Source emission timestamp")
    data_type: DataTypeLiteral = Field(..., description="forecast, observation, advisory, warning, or static")
    valid_time: str = Field(..., description="Validity window or validity timestamp")
    retrieved_at: str = Field(..., description="Exact time ORCA backend retrieved the record")
    quality: str = Field(default="available", description="Data quality indicator")
    source_url: str = Field(..., description="Official authoritative source URL")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Supplementary source parameters")

class MarineZoneCondition(BaseModel):
    waveHeight: str
    waveState: str
    windSpeed: str
    windDirection: str
    seaSurfaceTemp: str
    chlorophyll: str
    marineWarning: bool
    marineWarningText: Optional[str] = None
    geofenceStatus: str
    isRestricted: bool

class MarineZoneModel(BaseModel):
    id: str
    code: str
    name: str
    status: Literal["high_risk", "caution", "suitable", "restricted"]
    statusLabel: str
    riskScore: int
    confidence: Literal["High", "Medium", "Low"]
    coordinates: List[List[float]] # [[lat, lon], ...]
    center: List[float] # [lat, lon]
    depthMeters: str
    distanceCoastKm: int
    conditions: MarineZoneCondition
    reasons: List[str]
    recommendation: str
    bestTimeToVisit: Optional[str] = None
    pfzAdvisoryStatus: str
    dataSourceSummary: str
    primarySourceId: str
    sourceUrl: str

class QueryRequirement(BaseModel):
    intent: str
    location: Dict[str, Any]
    time_window: Dict[str, Any]
    required_sources: List[str]

class MarineForecastResponse(BaseModel):
    records: List[NormalizedMarineRecord]
    retrieved_at: str
    source_count: int
    coverage_area: str

class MarineWarningsResponse(BaseModel):
    warnings_active: bool
    bulletins: List[Dict[str, Any]]
    retrieved_at: str
    source_url: str
