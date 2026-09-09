"""
Generic ERDDAP Response Parser for INCOIS JSON Subsets.
Parses tabular & gridded ERDDAP JSON outputs into structured records with null/NaN safety.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import math

@dataclass
class ParsedERDDAPRecord:
    timestamp: str
    latitude: float
    longitude: float
    parameter: str
    variable_name: str
    value: Any
    unit: str
    is_valid: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ParsedERDDAPTable:
    dataset_id: str
    column_names: List[str]
    column_types: List[str]
    column_units: List[str]
    records: List[ParsedERDDAPRecord]
    row_count: int
    missing_value_count: int
    status: str = "SUCCESS"

class ERDDAPResponseParser:
    """
    Parses standard ERDDAP JSON response payloads:
    {
      "table": {
        "columnNames": [...],
        "columnTypes": [...],
        "columnUnits": [...],
        "rows": [[...], [...]]
      }
    }
    """
    def parse_json(
        self,
        dataset_id: str,
        payload: Dict[str, Any],
        source_url: str = ""
    ) -> ParsedERDDAPTable:
        table_data = payload.get("table", {})
        if not table_data:
            return ParsedERDDAPTable(
                dataset_id=dataset_id,
                column_names=[],
                column_types=[],
                column_units=[],
                records=[],
                row_count=0,
                missing_value_count=0,
                status="EMPTY"
            )

        col_names = table_data.get("columnNames", [])
        col_types = table_data.get("columnTypes", [])
        col_units = table_data.get("columnUnits", [])
        raw_rows = table_data.get("rows", [])

        # Index coordinates & time columns
        time_idx = next((i for i, c in enumerate(col_names) if c in ("time", "valid_date", "date")), None)
        lat_idx = next((i for i, c in enumerate(col_names) if c in ("latitude", "lat")), None)
        lon_idx = next((i for i, c in enumerate(col_names) if c in ("longitude", "lon")), None)

        parsed_records: List[ParsedERDDAPRecord] = []
        missing_count = 0

        for row in raw_rows:
            time_val = str(row[time_idx]) if time_idx is not None and time_idx < len(row) else ""
            try:
                lat_val = float(row[lat_idx]) if lat_idx is not None and lat_idx < len(row) and row[lat_idx] is not None else 0.0
                lon_val = float(row[lon_idx]) if lon_idx is not None and lon_idx < len(row) and row[lon_idx] is not None else 0.0
            except (ValueError, TypeError):
                lat_val, lon_val = 0.0, 0.0

            # Parse each variable column (non-coordinate)
            for idx, col_name in enumerate(col_names):
                if idx in (time_idx, lat_idx, lon_idx):
                    continue

                raw_val = row[idx] if idx < len(row) else None
                unit = col_units[idx] if idx < len(col_units) and col_units[idx] else "unitless"

                # Missing value / NaN detection
                is_missing = False
                if raw_val is None or raw_val == "NaN" or raw_val == "":
                    is_missing = True
                    missing_count += 1
                elif isinstance(raw_val, (int, float)):
                    if math.isnan(raw_val) or raw_val in (-9999.0, -999.0, 9999.0):
                        is_missing = True
                        missing_count += 1

                parsed_records.append(ParsedERDDAPRecord(
                    timestamp=time_val,
                    latitude=lat_val,
                    longitude=lon_val,
                    parameter=self._normalize_parameter_name(col_name),
                    variable_name=col_name,
                    value=None if is_missing else raw_val,
                    unit=unit,
                    is_valid=not is_missing,
                    metadata={"source_url": source_url, "column_type": col_types[idx] if idx < len(col_types) else "unknown"}
                ))

        return ParsedERDDAPTable(
            dataset_id=dataset_id,
            column_names=col_names,
            column_types=col_types,
            column_units=col_units,
            records=parsed_records,
            row_count=len(raw_rows),
            missing_value_count=missing_count,
            status="SUCCESS" if parsed_records else "NO_DATA"
        )

    def _normalize_parameter_name(self, col_name: str) -> str:
        mapping = {
            "swh": "significant_wave_height",
            "mwp": "mean_wave_period",
            "mwd": "mean_wave_direction",
            "swell_height": "swell_wave_height",
            "shww": "wind_wave_height",
            "sst": "sea_surface_temperature",
            "sst_anomaly": "sea_surface_temperature_anomaly",
            "temp": "sea_surface_temperature",
            "u": "surface_eastward_current",
            "v": "surface_northward_current",
            "chlorophyll": "chlorophyll_concentration",
            "kd_490": "diffuse_attenuation_coefficient"
        }
        return mapping.get(col_name.lower(), col_name.lower())

response_parser = ERDDAPResponseParser()

# Backward-compatible parsers
from datetime import datetime, timezone
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
            "cadence": "Daily satellite composite"
        }
    )

