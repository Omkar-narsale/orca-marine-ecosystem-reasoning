"""
Bhuvan GIS Query Builder.
Constructs and validates requests for official Bhuvan NRSC geospatial endpoints.
"""

from typing import Dict, Any, Optional

class BhuvanQueryBuilder:
    def __init__(self, base_url: str = "https://bhuvan-app1.nrsc.gov.in/api"):
        self.base_url = base_url.rstrip('/')

    def build_geocode_query(self, location_name: str, state: Optional[str] = None) -> Dict[str, Any]:
        """Builds validated village/location geocoding request."""
        if not location_name or not location_name.strip():
            raise ValueError("location_name required for Bhuvan geocoding")
        params = {"query": location_name.strip()}
        if state:
            params["state"] = state.strip()
        return {
            "endpoint": "/geocode/village",
            "method": "GET",
            "params": params,
            "url": f"{self.base_url}/geocode/village?val={location_name.strip()}"
        }

    def build_reverse_geocode_query(self, lat: float, lon: float) -> Dict[str, Any]:
        """Builds validated reverse geocoding request."""
        if lat < -90.0 or lat > 90.0 or lon < -180.0 or lon > 180.0:
            raise ValueError(f"Invalid coordinates ({lat}, {lon})")
        return {
            "endpoint": "/reverse/village",
            "method": "GET",
            "params": {"lat": round(lat, 4), "lon": round(lon, 4)},
            "url": f"{self.base_url}/reverse/village?lat={round(lat, 4)}&lon={round(lon, 4)}"
        }

    def build_route_query(self, origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float) -> Dict[str, Any]:
        """Builds validated shortest path routing request."""
        return {
            "endpoint": "/routing/shortest_path",
            "method": "GET",
            "params": {
                "origin": f"{round(origin_lat, 4)},{round(origin_lon, 4)}",
                "dest": f"{round(dest_lat, 4)},{round(dest_lon, 4)}"
            },
            "url": f"{self.base_url}/routing/shortest_path?orig={origin_lat},{origin_lon}&dest={dest_lat},{dest_lon}"
        }

bhuvan_query_builder = BhuvanQueryBuilder()
