"""
INCOIS ERDDAP Query Builder with Dimension Constraints & Safety Limits.
Builds strictly valid, dimension-compliant griddap and tabledap URLs.
Documentation: https://erddap.incois.gov.in/erddap/griddap/documentation.html
"""

import urllib.parse
from typing import List, Dict, Any, Optional
from backend.app.services.incois.datasets import INCOISDatasetMetadata
from backend.app.core.config import settings

# Query Size & Safety Guardrails
MAX_LAT_SPAN_DEG = 5.0
MAX_LON_SPAN_DEG = 5.0
MAX_TIME_SPAN_DAYS = 7.0
MAX_VARIABLES_PER_REQUEST = 8

class ERDDAPQueryBuilder:
    def __init__(self, base_url: str = settings.INCOIS_ERDDAP_URL):
        self.base_url = base_url.rstrip('/')

    def build_griddap_query(
        self,
        dataset_meta: INCOISDatasetMetadata,
        variables: List[str],
        start_time_utc: str,
        end_time_utc: str,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float,
        stride: int = 1
    ) -> str:
        """
        Builds a dimensionally aligned griddap subset URL.
        Example syntax:
        https://erddap.incois.gov.in/erddap/griddap/DATASET.json?var1[(start):stride:(end)][(min_lat):stride:(max_lat)][(min_lon):stride:(max_lon)],var2...
        """
        # 1. Safety & Bounds Validation
        lat_span = abs(max_lat - min_lat)
        lon_span = abs(max_lon - min_lon)

        if lat_span > MAX_LAT_SPAN_DEG:
            mid_lat = (min_lat + max_lat) / 2.0
            min_lat = mid_lat - (MAX_LAT_SPAN_DEG / 2.0)
            max_lat = mid_lat + (MAX_LAT_SPAN_DEG / 2.0)

        if lon_span > MAX_LON_SPAN_DEG:
            mid_lon = (min_lon + max_lon) / 2.0
            min_lon = mid_lon - (MAX_LON_SPAN_DEG / 2.0)
            max_lon = mid_lon + (MAX_LON_SPAN_DEG / 2.0)

        # Ensure min <= max
        actual_min_lat = min(min_lat, max_lat)
        actual_max_lat = max(min_lat, max_lat)
        actual_min_lon = min(min_lon, max_lon)
        actual_max_lon = max(min_lon, max_lon)

        # 2. Filter allowed variables from dataset metadata
        valid_vars = [v for v in variables if v in dataset_meta.variables][:MAX_VARIABLES_PER_REQUEST]
        if not valid_vars:
            valid_vars = list(dataset_meta.variables.keys())[:2]

        # 3. Build dimension constraint clauses following dataset dimension order
        dim_clauses = []
        for dim in dataset_meta.dimensions:
            if dim == "time":
                dim_clauses.append(f"[({start_time_utc}):1:({end_time_utc})]")
            elif dim in ("latitude", "lat"):
                dim_clauses.append(f"[({actual_min_lat}):{stride}:({actual_max_lat})]")
            elif dim in ("longitude", "lon"):
                dim_clauses.append(f"[({actual_min_lon}):{stride}:({actual_max_lon})]")
            elif dim in ("altitude", "depth"):
                dim_clauses.append("[(0.0):1:(0.0)]")

        dim_str = "".join(dim_clauses)
        var_expressions = [f"{v}{dim_str}" for v in valid_vars]
        query_string = ",".join(var_expressions)

        endpoint = f"{self.base_url}/griddap/{dataset_meta.dataset_id}.json?{query_string}"
        return endpoint

    def build_tabledap_query(
        self,
        dataset_meta: INCOISDatasetMetadata,
        variables: List[str],
        start_time_utc: Optional[str] = None,
        min_lat: Optional[float] = None,
        max_lat: Optional[float] = None,
        min_lon: Optional[float] = None,
        max_lon: Optional[float] = None
    ) -> str:
        """
        Builds a tabledap JSON query URL with constraint parameters.
        """
        valid_vars = [v for v in variables if v in dataset_meta.variables] or list(dataset_meta.variables.keys())
        query = ",".join(valid_vars)
        url = f"{self.base_url}/tabledap/{dataset_meta.dataset_id}.json?{query}"

        constraints = []
        if start_time_utc:
            constraints.append(f"time>={start_time_utc}")
        if min_lat is not None and max_lat is not None:
            constraints.append(f"latitude>={min_lat}&latitude<={max_lat}")
        if min_lon is not None and max_lon is not None:
            constraints.append(f"longitude>={min_lon}&longitude<={max_lon}")

        if constraints:
            url += "&" + "&".join(constraints)

        return url

query_builder = ERDDAPQueryBuilder()
