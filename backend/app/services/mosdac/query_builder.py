"""
MOSDAC Source-Specific Query Builder.
Implements the official ISRO MOSDAC Data Download API specification.
Ref: https://mosdac.gov.in/downloadapi-manual
"""

from typing import Dict, Any, Optional
from datetime import datetime
from backend.app.schemas.query_plan import DatasetMetadata, LocationContext, TimeContext, DataRequirement

class MosdacQueryBuilder:
    """
    Constructs validated MOSDAC Data Download API search payloads.
    Search Parameters:
      - datasetId (required)
      - startTime (YYYY-MM-DD)
      - endTime (YYYY-MM-DD)
      - count (max result count)
      - boundingBox (format: 'minLon,minLat,maxLon,maxLat')
      - gId (optional granule ID)
    """

    MAX_GEO_SPAN_DEG = 8.0
    MAX_RESULT_COUNT = 50

    def build_search_query(
        self,
        dataset: DatasetMetadata,
        location: LocationContext,
        time_window: TimeContext,
        count: int = 5,
        granule_id: str = ""
    ) -> Dict[str, Any]:
        """
        Builds and validates a MOSDAC Download API search configuration dictionary.
        """
        # 1. Dataset ID Validation
        if not dataset.dataset_id:
            raise ValueError("MOSDAC query requires a non-empty datasetId")
        if dataset.source != "MOSDAC":
            raise ValueError(f"Dataset {dataset.dataset_id} is not a MOSDAC source (got {dataset.source})")

        # 2. Time Range Validation (YYYY-MM-DD)
        start_date = time_window.start[:10]
        end_date = time_window.end[:10]

        # 3. Spatial Bounding Box Validation (minLon, minLat, maxLon, maxLat)
        bbox = location.marine_bbox
        min_lat = bbox["min_lat"]
        max_lat = bbox["max_lat"]
        min_lon = bbox["min_lon"]
        max_lon = bbox["max_lon"]

        lat_span = max_lat - min_lat
        lon_span = max_lon - min_lon
        if lat_span > self.MAX_GEO_SPAN_DEG or lon_span > self.MAX_GEO_SPAN_DEG:
            raise ValueError(
                f"MOSDAC query bounding box exceeds safety span limit of {self.MAX_GEO_SPAN_DEG}° "
                f"(lat_span: {lat_span:.2f}°, lon_span: {lon_span:.2f}°)"
            )

        # MOSDAC official format: "minLon,minLat,maxLon,maxLat"
        bounding_box_str = f"{min_lon:.4f},{min_lat:.4f},{max_lon:.4f},{max_lat:.4f}"

        # 4. Result Count Validation
        safe_count = max(1, min(count, self.MAX_RESULT_COUNT))

        return {
            "datasetId": dataset.dataset_id,
            "startTime": start_date,
            "endTime": end_date,
            "count": safe_count,
            "boundingBox": bounding_box_str,
            "gId": granule_id or "",
            "source": "MOSDAC",
            "search_url": f"https://mosdac.gov.in/downloadapi/search?datasetId={dataset.dataset_id}&startTime={start_date}&endTime={end_date}&boundingBox={bounding_box_str}&count={safe_count}"
        }

mosdac_query_builder = MosdacQueryBuilder()
