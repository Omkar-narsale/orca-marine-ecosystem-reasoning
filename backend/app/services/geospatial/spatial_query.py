from typing import List, Dict, Any, Optional
from shapely.geometry import Polygon, Point
from backend.app.schemas.marine import NormalizedMarineRecord
from backend.app.services.geospatial.geometry import (
    create_polygon_from_coords,
    point_in_polygon,
    haversine_distance_km
)

def align_records_to_zone(
    zone_coords: List[List[float]],
    records: List[NormalizedMarineRecord],
    max_search_radius_km: float = 35.0
) -> List[NormalizedMarineRecord]:
    """
    Spatially filters and aligns normalized marine records to a specific zone polygon.
    First checks exact point-in-polygon containment; if empty, finds records within nearest distance radius.
    """
    try:
        zone_poly = create_polygon_from_coords(zone_coords)
    except Exception:
        return []

    centroid_y = zone_poly.centroid.y # lat
    centroid_x = zone_poly.centroid.x # lon

    inside_records: List[NormalizedMarineRecord] = []
    nearby_records: List[Tuple[float, NormalizedMarineRecord]] = []

    for rec in records:
        if rec.latitude is None or rec.longitude is None:
            # Regional advisory without exact point
            inside_records.append(rec)
            continue

        if point_in_polygon(rec.latitude, rec.longitude, zone_poly):
            inside_records.append(rec)
        else:
            dist_km = haversine_distance_km(centroid_y, centroid_x, rec.latitude, rec.longitude)
            if dist_km <= max_search_radius_km:
                nearby_records.append((dist_km, rec))

    if inside_records:
        return inside_records

    # Return nearest records sorted by distance
    nearby_records.sort(key=lambda x: x[0])
    return [r[1] for r in nearby_records]
