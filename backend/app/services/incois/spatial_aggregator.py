"""
Spatial Aggregator for INCOIS Gridded ERDDAP Outputs.
Computes nearest-point extractions, spatial bounding box statistics, and candidate zone intersections.
"""

import math
from typing import List, Dict, Any, Optional
from backend.app.schemas.marine import NormalizedMarineRecord

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in km."""
    r = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return r * c

class SpatialAggregator:
    def get_nearest_point_records(
        self,
        records: List[NormalizedMarineRecord],
        target_lat: float,
        target_lon: float
    ) -> List[NormalizedMarineRecord]:
        """
        Extracts records for the nearest grid point to target coordinates for each parameter.
        """
        if not records:
            return []

        # Group by parameter
        by_param: Dict[str, List[NormalizedMarineRecord]] = {}
        for r in records:
            if r.value is not None and isinstance(r.value, (int, float)):
                if r.parameter not in by_param:
                    by_param[r.parameter] = []
                by_param[r.parameter].append(r)

        result: List[NormalizedMarineRecord] = []
        for param, param_recs in by_param.items():
            nearest = min(
                param_recs,
                key=lambda r: haversine_distance_km(target_lat, target_lon, r.latitude, r.longitude)
            )
            result.append(nearest)

        return result

    def compute_spatial_summary(
        self,
        records: List[NormalizedMarineRecord],
        parameter: str
    ) -> Dict[str, Any]:
        """
        Computes spatial min, max, mean, and cell count for a parameter across a bounding box.
        """
        param_recs = [r for r in records if r.parameter == parameter and isinstance(r.value, (int, float))]
        if not param_recs:
            return {"count": 0, "mean": None, "min": None, "max": None}

        values = [r.value for r in param_recs]
        return {
            "parameter": parameter,
            "unit": param_recs[0].unit,
            "count": len(values),
            "mean": round(sum(values) / len(values), 2),
            "min": round(min(values), 2),
            "max": round(max(values), 2),
            "representative_lat": param_recs[0].latitude,
            "representative_lon": param_recs[0].longitude
        }

spatial_aggregator = SpatialAggregator()
