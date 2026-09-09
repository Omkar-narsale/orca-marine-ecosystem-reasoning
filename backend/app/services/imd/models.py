"""
IMD Pydantic Models & Schemas for Official Meteorological & Cyclone APIs.
Ref: https://api.imd.gov.in/public/api_reference.html
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class IMDCurrentWeather(BaseModel):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    observation_time: str
    temperature_c: float
    humidity_pct: float
    wind_speed_kt: float
    wind_direction: str
    surface_pressure_hpa: Optional[float] = None
    visibility_km: Optional[float] = None
    weather_condition: str = "Fair"

class IMDDayForecast(BaseModel):
    forecast_date: str
    min_temp_c: float
    max_temp_c: float
    wind_speed_kt: float
    wind_direction: str
    weather_summary: str
    rainfall_probability: Optional[str] = None

class IMDCityForecast(BaseModel):
    station_id: str
    station_name: str
    latitude: float
    longitude: float
    issue_time: str
    forecasts: List[IMDDayForecast] = Field(default_factory=list)

class IMDDistrictNowcast(BaseModel):
    district_id: str
    district_name: str
    state: str
    issue_time: str
    valid_until: str
    nowcast_text: str
    severity_level: str = "Moderate"

class IMDDistrictWarning(BaseModel):
    district_id: str
    district_name: str
    state: str
    warning_date: str
    warning_colour: str = "Green"  # Green, Yellow, Orange, Red
    warning_type: str = "Nil Warning"
    warning_description: str = ""

class IMDSeaAreaBulletin(BaseModel):
    sea_area: str  # e.g., North Arabian Sea, South East Arabian Sea, Southwest Bay of Bengal
    issue_time: str
    valid_until: str
    synoptic_situation: str
    wind_speed_kt: float
    wind_direction: str
    weather_condition: str
    sea_state: str

class IMDCoastalBulletin(BaseModel):
    coastal_zone: str  # e.g., North Maharashtra Coast, South Gujarat Coast, Tamil Nadu Coast
    issue_time: str
    valid_until: str
    wind_speed_kt: float
    wind_direction: str
    gusts_kt: float
    weather_condition: str
    port_warning: Optional[str] = None

class IMDFishermenWarning(BaseModel):
    coastal_region: str
    issue_time: str
    valid_until: str
    is_active: bool = True
    severity: str = "Advisory"  # Warning, High Alert, Squall Warning
    wind_speed_range_kt: str = "25-35"
    headline: str
    instructions: str
    port_signals: Optional[str] = None

class IMDCycloneTrackPoint(BaseModel):
    time_utc: str
    latitude: float
    longitude: float
    category: str
    max_wind_kt: float
    gusts_kt: float
    central_pressure_hpa: float

class IMDCycloneTrack(BaseModel):
    cyclone_id: str
    name: str
    issue_time: str
    current_category: str
    track_points: List[IMDCycloneTrackPoint] = Field(default_factory=list)

class IMDCycloneWind(BaseModel):
    cyclone_id: str
    name: str
    issue_time: str
    quadrants_nm: Dict[str, Any] = Field(default_factory=dict)
    wind_polygon: List[List[float]] = Field(default_factory=list, description="[[lat, lon], ...] polygon boundary")

class IMDCycloneCone(BaseModel):
    cyclone_id: str
    name: str
    issue_time: str
    valid_until: str
    cone_polygon: List[List[float]] = Field(default_factory=list, description="[[lat, lon], ...] uncertainty cone")
