"""
IMD Data Normalizer.
Converts structured IMD meteorological models & warnings into ORCA NormalizedMarineRecords with official authority tagging.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.schemas.query_plan import AuthorityType, LocationContext, TimeContext, DatasetMetadata
from backend.app.services.imd.models import (
    IMDCurrentWeather,
    IMDCityForecast,
    IMDDistrictWarning,
    IMDFishermenWarning,
    IMDCoastalBulletin,
    IMDSeaAreaBulletin,
    IMDCycloneTrack,
    IMDCycloneWind,
    IMDCycloneCone
)
from backend.app.core.config import settings

class IMDNormalizer:
    def normalize_current_weather(self, data: IMDCurrentWeather, source_url: str = "") -> List[NormalizedMarineRecord]:
        now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")
        return [
            NormalizedMarineRecord(
                source="IMD",
                source_id="IMD_MARINE",
                parameter="surface_wind_10m",
                value=data.wind_speed_kt,
                unit="kt",
                latitude=data.latitude,
                longitude=data.longitude,
                timestamp=data.observation_time,
                observation_time=data.observation_time,
                data_type="observation",
                valid_time=f"Observation · {data.station_name} Current WX",
                retrieved_at=now_ist,
                quality="verified",
                source_url=source_url or f"{settings.IMD_API_BASE_URL}/api/v1/current_wx",
                metadata={
                    "station_id": data.station_id,
                    "direction": data.wind_direction,
                    "temperature_c": data.temperature_c,
                    "humidity_pct": data.humidity_pct,
                    "condition": data.weather_condition,
                    "authority_type": AuthorityType.OFFICIAL_OBSERVATION.value
                }
            )
        ]

    def normalize_fishermen_warning(self, data: IMDFishermenWarning, lat: float, lon: float, source_url: str = "") -> List[NormalizedMarineRecord]:
        now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")
        now_utc = datetime.now(timezone.utc).isoformat()
        return [
            NormalizedMarineRecord(
                source="IMD",
                source_id="IMD_MARINE",
                parameter="marine_fishermen_warning",
                value=data.headline,
                unit="bulletin_alert",
                latitude=lat,
                longitude=lon,
                timestamp=data.issue_time or now_utc,
                data_type="warning",
                valid_time=f"Warning · {data.valid_until}",
                retrieved_at=now_ist,
                quality="verified",
                source_url=source_url or f"{settings.IMD_API_BASE_URL}/api/v1/fishermenwarning",
                metadata={
                    "coastal_region": data.coastal_region,
                    "severity": data.severity,
                    "instructions": data.instructions,
                    "port_signals": data.port_signals,
                    "speed_range_kt": data.wind_speed_range_kt,
                    "authority_type": AuthorityType.OFFICIAL_WARNING.value
                }
            )
        ]

    def normalize_coastal_bulletin(self, data: IMDCoastalBulletin, lat: float, lon: float, source_url: str = "") -> List[NormalizedMarineRecord]:
        now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")
        now_utc = datetime.now(timezone.utc).isoformat()
        return [
            NormalizedMarineRecord(
                source="IMD",
                source_id="IMD_MARINE",
                parameter="surface_wind_10m",
                value=data.wind_speed_kt,
                unit="kt",
                latitude=lat,
                longitude=lon,
                timestamp=data.issue_time or now_utc,
                data_type="forecast",
                valid_time=f"Forecast · {data.valid_until}",
                retrieved_at=now_ist,
                quality="verified",
                source_url=source_url or f"{settings.IMD_API_BASE_URL}/api/v1/coastalbulletin",
                metadata={
                    "coastal_zone": data.coastal_zone,
                    "direction": data.wind_direction,
                    "gusts_kt": data.gusts_kt,
                    "weather_condition": data.weather_condition,
                    "port_warning": data.port_warning,
                    "authority_type": AuthorityType.OFFICIAL_FORECAST.value
                }
            )
        ]

    def normalize_district_warning(self, data: IMDDistrictWarning, lat: float, lon: float, source_url: str = "") -> List[NormalizedMarineRecord]:
        now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")
        now_utc = datetime.now(timezone.utc).isoformat()
        return [
            NormalizedMarineRecord(
                source="IMD",
                source_id="IMD_MARINE",
                parameter="district_weather_warning",
                value=f"{data.warning_colour} Alert: {data.warning_type}",
                unit="warning_color_code",
                latitude=lat,
                longitude=lon,
                timestamp=now_utc,
                data_type="warning",
                valid_time=f"Warning · Valid {data.warning_date}",
                retrieved_at=now_ist,
                quality="verified",
                source_url=source_url or f"{settings.IMD_API_BASE_URL}/api/v1/districtwarning",
                metadata={
                    "district_id": data.district_id,
                    "district_name": data.district_name,
                    "warning_colour": data.warning_colour,
                    "warning_description": data.warning_description,
                    "authority_type": AuthorityType.OFFICIAL_WARNING.value
                }
            )
        ]

imd_normalizer = IMDNormalizer()
