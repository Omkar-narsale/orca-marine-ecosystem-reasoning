import math
from typing import List, Tuple, Dict, Any, Optional, Union
from shapely.geometry import Point, Polygon, MultiPolygon, box
from shapely.ops import unary_union

def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on the earth in kilometers."""
    R = 6371.0 # Earth radius in kilometers
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2.0) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2.0) ** 2
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def create_polygon_from_coords(coords: List[List[float]]) -> Polygon:
    """
    Creates a Shapely Polygon from a list of [lat, lon] coordinates.
    Expects coordinates in [[lat, lon], ...]. Converts to (lon, lat) internally for GIS Cartesian plane.
    """
    if len(coords) < 3:
        raise ValueError("Polygon requires at least 3 vertices")
    # In GIS standard, (x, y) = (lon, lat)
    xy_coords = [(pt[1], pt[0]) for pt in coords]
    return Polygon(xy_coords)

# Alias for convenience
create_polygon = create_polygon_from_coords

def point_in_polygon(lat: float, lon: float, poly: Union[Polygon, List[List[float]]]) -> bool:
    """Check if a point (lat, lon) is contained inside a polygon or list of coordinates."""
    if isinstance(poly, list):
        poly = create_polygon_from_coords(poly)
    pt = Point(lon, lat)
    return poly.contains(pt) or poly.touches(pt)

def calculate_polygon_intersection(
    poly1: Union[Polygon, List[List[float]]],
    poly2: Union[Polygon, List[List[float]]]
) -> Dict[str, Any]:
    """
    Calculates spatial intersection between two polygons.
    Returns dict:
      intersects: bool
      intersection_type: 'NO_INTERSECTION' | 'PARTIAL_INTERSECTION' | 'FULL_INTERSECTION'
      overlap_percentage: float (0.0 to 100.0)
      area_sq_deg: float
    """
    if isinstance(poly1, list):
        poly1 = create_polygon_from_coords(poly1)
    if isinstance(poly2, list):
        poly2 = create_polygon_from_coords(poly2)

    if not poly1.intersects(poly2):
        return {
            "intersects": False,
            "intersection_type": "NO_INTERSECTION",
            "overlap_percentage": 0.0,
            "area_sq_deg": 0.0
        }

    intersection = poly1.intersection(poly2)
    if intersection.is_empty:
        return {
            "intersects": False,
            "intersection_type": "NO_INTERSECTION",
            "overlap_percentage": 0.0,
            "area_sq_deg": 0.0
        }

    poly1_area = poly1.area
    if poly1_area <= 0:
        return {
            "intersects": False,
            "intersection_type": "NO_INTERSECTION",
            "overlap_percentage": 0.0,
            "area_sq_deg": 0.0
        }

    overlap_ratio = intersection.area / poly1_area
    overlap_pct = round(overlap_ratio * 100.0, 1)

    if overlap_pct >= 95.0:
        itype = "FULL_INTERSECTION"
    elif overlap_pct > 0.01:
        itype = "PARTIAL_INTERSECTION"
    else:
        itype = "NO_INTERSECTION"

    return {
        "intersects": itype != "NO_INTERSECTION",
        "intersection_type": itype,
        "overlap_percentage": overlap_pct,
        "area_sq_deg": round(intersection.area, 6)
    }

def calculate_centroid(coords: List[List[float]]) -> Tuple[float, float]:
    """Returns [centroid_lat, centroid_lon] from polygon coordinate list."""
    poly = create_polygon_from_coords(coords)
    c = poly.centroid
    return (round(c.y, 4), round(c.x, 4))
