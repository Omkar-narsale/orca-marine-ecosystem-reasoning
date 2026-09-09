"""
Bhuvan Geocoding, Reverse Geocoding & Routing Data Models.
Ref: https://bhuvan-app1.nrsc.gov.in/api/
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BhuvanGeocodeResult(BaseModel):
    location_name: str
    latitude: float
    longitude: float
    district: Optional[str] = None
    state: Optional[str] = None
    pincode: Optional[str] = None
    confidence: float = 1.0
    source: str = "BHUVAN"
    authority: str = "OFFICIAL_GOVERNMENT_GIS"

class BhuvanReverseGeocodeResult(BaseModel):
    latitude: float
    longitude: float
    village: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    distance_to_settlement_km: Optional[float] = None
    source: str = "BHUVAN"
    authority: str = "OFFICIAL_GOVERNMENT_GIS"

class BhuvanShortestPathResult(BaseModel):
    origin: Dict[str, float]
    destination: Dict[str, float]
    distance_km: float
    duration_min: float
    path_coordinates: List[List[float]] = Field(default_factory=list, description="[[lat, lon], ...]")
    source: str = "BHUVAN"
