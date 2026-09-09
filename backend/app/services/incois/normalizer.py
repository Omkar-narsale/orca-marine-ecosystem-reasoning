"""
INCOIS Marine Record Normalizer.
Transforms parsed ERDDAP rows into standard ORCA NormalizedMarineRecord schemas with full source provenance.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.services.incois.parser import ParsedERDDAPRecord
from backend.app.services.incois.datasets import INCOISDatasetMetadata

class ERDDAPNormalizer:
    def normalize_record(
        self,
        record: ParsedERDDAPRecord,
        dataset_meta: INCOISDatasetMetadata,
        source_url: str = ""
    ) -> NormalizedMarineRecord:
        now_ist = datetime.now().strftime("%d %b %Y %H:%M IST")

        # Map dataset data_type to lowercase schema format
        data_type_lower = dataset_meta.data_type.lower()
        if data_type_lower not in ("forecast", "observation", "advisory", "warning", "static", "cached"):
            data_type_lower = "forecast"

        # Standardize units
        unit_str = record.unit
        if unit_str == "degree_C":
            unit_str = "°C"
        elif unit_str in ("m s-1", "m/s"):
            unit_str = "m/s"
        elif unit_str == "mg m-3":
            unit_str = "mg/m³"

        # Format human-readable valid_time
        valid_label = record.timestamp
        if record.timestamp:
            try:
                # Format ISO UTC timestamp to IST display string
                dt = datetime.fromisoformat(record.timestamp.replace("Z", "+00:00"))
                valid_label = f"{dt.strftime('%d %b %Y %H:%M UTC')} ({dataset_meta.data_type.capitalize()})"
            except Exception:
                valid_label = f"{record.timestamp} ({dataset_meta.data_type.capitalize()})"
        else:
            valid_label = f"Latest Available ({dataset_meta.data_type.capitalize()})"

        quality_label = "verified" if record.is_valid else "degraded"

        return NormalizedMarineRecord(
            source="INCOIS",
            source_id="INCOIS_ERDDAP",
            parameter=record.parameter,
            value=record.value,
            unit=unit_str,
            latitude=record.latitude,
            longitude=record.longitude,
            timestamp=record.timestamp or datetime.now(timezone.utc).isoformat(),
            data_type=data_type_lower,
            valid_time=valid_label,
            retrieved_at=now_ist,
            quality=quality_label,
            source_url=source_url or dataset_meta.official_url,
            metadata={
                "dataset_id": dataset_meta.dataset_id,
                "dataset_title": dataset_meta.title,
                "raw_variable": record.variable_name,
                "data_semantics": dataset_meta.data_type,
                "spatial_resolution_deg": dataset_meta.spatial_resolution_deg
            }
        )

    def normalize_records(
        self,
        records: List[ParsedERDDAPRecord],
        dataset_meta: INCOISDatasetMetadata,
        source_url: str = ""
    ) -> List[NormalizedMarineRecord]:
        return [self.normalize_record(r, dataset_meta, source_url) for r in records if r.is_valid]

normalizer = ERDDAPNormalizer()
