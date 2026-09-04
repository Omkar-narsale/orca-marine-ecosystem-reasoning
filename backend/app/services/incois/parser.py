from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.core.config import settings

def parse_incois_wave_record(
    lat: float,
    lon: float,
    wave_height_m: float,
    wave_period_s: Optional[float] = None,
    wave_direction_deg: Optional[float] = None,
    emission_time: Optional[str] = None,
    valid_time: Optional[str] = None
) -> NormalizedMarineRecord:
    now_utc = datetime.now(timezone.utc).isoformat()
    now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")
    
    return NormalizedMarineRecord(
        source="INCOIS",
        source_id="INCOIS_OSF",
        parameter="significant_wave_height",
        value=round(wave_height_m, 2),
        unit="m",
        latitude=lat,
        longitude=lon,
        timestamp=emission_time or now_utc,
        data_type="forecast",
        valid_time=valid_time or "Forecast · Valid Tomorrow 06:00 IST",
        retrieved_at=now_ist,
        quality="verified",
        source_url=settings.INCOIS_OSF_URL,
        metadata={
            "model": "Wave Watch III / ROMS Coastal Grid",
            "wave_period_sec": wave_period_s,
            "wave_direction_deg": wave_direction_deg,
            "cadence": "12-hourly numerical cycle"
        }
    )

def parse_incois_sst_record(
    lat: float,
    lon: float,
    sst_celsius: float,
    emission_time: Optional[str] = None,
    valid_time: Optional[str] = None
) -> NormalizedMarineRecord:
    now_utc = datetime.now(timezone.utc).isoformat()
    now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")

    return NormalizedMarineRecord(
        source="INCOIS",
        source_id="INCOIS_OSF",
        parameter="sea_surface_temperature",
        value=round(sst_celsius, 1),
        unit="°C",
        latitude=lat,
        longitude=lon,
        timestamp=emission_time or now_utc,
        data_type="forecast",
        valid_time=valid_time or "Forecast · Valid Tomorrow 06:00 IST",
        retrieved_at=now_ist,
        quality="verified",
        source_url=settings.INCOIS_OSF_URL,
        metadata={
            "model": "ROMS 3D Ocean Model",
            "cadence": "6-hourly forecast step"
        }
    )

def parse_incois_pfz_advisory(
    sector_name: str,
    lat: float,
    lon: float,
    status: str,
    depth_m: str,
    bearing: str,
    distance_km: int
) -> NormalizedMarineRecord:
    now_utc = datetime.now(timezone.utc).isoformat()
    now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")

    return NormalizedMarineRecord(
        source="INCOIS",
        source_id="INCOIS_PFZ",
        parameter="potential_fishing_zone_advisory",
        value=status,
        unit="advisory_zone",
        latitude=lat,
        longitude=lon,
        timestamp=now_utc,
        data_type="advisory",
        valid_time="Advisory · Latest Available Sector Composite",
        retrieved_at=now_ist,
        quality="verified",
        source_url=settings.INCOIS_PFZ_URL,
        metadata={
            "sector": sector_name,
            "depth": depth_m,
            "bearing": bearing,
            "distance_from_shore_km": distance_km,
            "cadence": "Daily satellite composite (non-deterministic forecast)"
        }
    )
