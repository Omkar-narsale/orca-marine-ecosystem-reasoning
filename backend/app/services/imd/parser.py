from datetime import datetime, timezone
from typing import Optional, Dict, Any
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.core.config import settings

def parse_imd_wind_record(
    lat: float,
    lon: float,
    wind_speed_kt: float,
    wind_direction: str,
    gusts_kt: Optional[float] = None,
    emission_time: Optional[str] = None,
    valid_time: Optional[str] = None
) -> NormalizedMarineRecord:
    now_utc = datetime.now(timezone.utc).isoformat()
    now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")

    return NormalizedMarineRecord(
        source="IMD",
        source_id="IMD_MARINE",
        parameter="surface_wind_10m",
        value=wind_speed_kt,
        unit="kt",
        latitude=lat,
        longitude=lon,
        timestamp=emission_time or now_utc,
        data_type="forecast",
        valid_time=valid_time or "Forecast · Valid Tomorrow 06:00 IST",
        retrieved_at=now_ist,
        quality="verified",
        source_url=f"{settings.IMD_API_BASE_URL}/api_reference.html",
        metadata={
            "direction": wind_direction,
            "gusts_kt": gusts_kt,
            "bulletin_source": "IMD Coastal Weather Synopsis",
            "cadence": "3-hour model step"
        }
    )

def parse_imd_warning_record(
    sector_name: str,
    warning_type: str,
    severity: str,
    headline: str,
    instructions: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None
) -> NormalizedMarineRecord:
    now_utc = datetime.now(timezone.utc).isoformat()
    now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")

    return NormalizedMarineRecord(
        source="IMD",
        source_id="IMD_MARINE",
        parameter="marine_fishermen_warning",
        value=headline,
        unit="bulletin_alert",
        latitude=lat,
        longitude=lon,
        timestamp=now_utc,
        data_type="warning",
        valid_time="Warning · Active for Next 24-48h",
        retrieved_at=now_ist,
        quality="verified",
        source_url=f"{settings.IMD_API_BASE_URL}/api_reference.html",
        metadata={
            "sector": sector_name,
            "warning_type": warning_type,
            "severity": severity,
            "instructions": instructions,
            "issuing_office": "Regional Meteorological Centre, Mumbai"
        }
    )
