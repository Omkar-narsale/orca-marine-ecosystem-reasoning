"""
ORCA Deterministic Spatial Engine.
Executes exact geometric operations using Shapely, GeoPandas & PostGIS concepts.
Enforces zero LLM fabrication of geographic distances, intersections, or boundaries.
"""

from typing import List, Dict, Any, Optional, Tuple, Union
from shapely.geometry import Point, Polygon, LineString, box
from shapely.ops import nearest_points

from backend.app.services.geospatial.geometry import (
    haversine_distance_km,
    create_polygon_from_coords,
    point_in_polygon as pip_helper,
    calculate_polygon_intersection
)

class SpatialEngine:
    """
    Deterministic WHERE engine for ORCA.
    Evaluates spatial relationships, boundary inclusions, route crossings, and hazard geometry overlaps.
    """

    def point_in_polygon(self, lat: float, lon: float, poly: Union[Polygon, List[List[float]]]) -> bool:
        """Determines if a geographic point (lat, lon) is contained in polygon."""
        return pip_helper(lat, lon, poly)

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance in kilometers."""
        return round(haversine_distance_km(lat1, lon1, lat2, lon2), 2)

    def distance_to_coast(self, lat: float, lon: float) -> float:
        """
        Calculates minimum distance from a point to the nearest Indian baseline coast coordinates.
        """
        from backend.app.services.incois.location import COASTAL_LOCATION_REGISTRY
        min_d = 999999.0
        for name, loc in COASTAL_LOCATION_REGISTRY.items():
            d = haversine_distance_km(lat, lon, loc.latitude, loc.longitude)
            if d < min_d:
                min_d = d
        return round(min_d, 1)

    def distance_to_feature(self, lat: float, lon: float, feature_coords: List[List[float]]) -> float:
        """Calculates distance from point to centroid or boundary of a feature."""
        if len(feature_coords) < 3:
            if len(feature_coords) == 1:
                return self.calculate_distance(lat, lon, feature_coords[0][0], feature_coords[0][1])
            return 0.0
        poly = create_polygon_from_coords(feature_coords)
        pt = Point(lon, lat)
        if poly.contains(pt):
            return 0.0
        # Calculate distance to nearest point on exterior ring
        nearest_geom = nearest_points(poly, pt)[0]
        return round(haversine_distance_km(lat, lon, nearest_geom.y, nearest_geom.x), 2)

    def find_nearest(self, lat: float, lon: float, candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Finds nearest feature from a list of items with 'latitude'/'longitude' or 'lat'/'lon'."""
        if not candidates:
            return None
        best = None
        min_d = 999999.0
        for c in candidates:
            c_lat = c.get("latitude", c.get("lat"))
            c_lon = c.get("longitude", c.get("lon"))
            if c_lat is not None and c_lon is not None:
                d = haversine_distance_km(lat, lon, float(c_lat), float(c_lon))
                if d < min_d:
                    min_d = d
                    best = {**c, "distance_km": round(d, 2)}
        return best

    def intersect(
        self,
        poly1: Union[Polygon, List[List[float]]],
        poly2: Union[Polygon, List[List[float]]]
    ) -> Dict[str, Any]:
        """Calculates intersection metrics between two polygon geometries."""
        return calculate_polygon_intersection(poly1, poly2)

    def route_intersects(
        self,
        waypoints: List[List[float]],
        restricted_zones: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Evaluates whether a planned vessel corridor crosses any restricted or hazard polygons.
        """
        if len(waypoints) < 2:
            return []
        
        # In GIS, (x, y) = (lon, lat)
        line_coords = [(pt[1], pt[0]) for pt in waypoints]
        route_line = LineString(line_coords)

        violations = []
        for zone in restricted_zones:
            coords = zone.get("coordinates", zone.get("polygon", []))
            if len(coords) >= 3:
                poly = create_polygon_from_coords(coords)
                if route_line.intersects(poly):
                    inter = route_line.intersection(poly)
                    violations.append({
                        "zone_id": zone.get("id", zone.get("zone_id", "RESTRICTED")),
                        "name": zone.get("name", "Restricted Area"),
                        "restriction_type": zone.get("restriction_type", "PROHIBITED_TRANSIT"),
                        "crosses_boundary": True,
                        "intersection_length_deg": round(inter.length, 6) if hasattr(inter, "length") else 0.0
                    })
        return violations

spatial_engine = SpatialEngine()
