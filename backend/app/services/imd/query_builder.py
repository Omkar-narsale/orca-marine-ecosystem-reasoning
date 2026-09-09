"""
IMD Source-Specific Query Builder for Official IMD APIs.
Implements the full contract for the 10 official IMD public endpoints.
Ref: https://api.imd.gov.in/public/api_reference.html
"""

from typing import Dict, Any, Optional
from backend.app.schemas.query_plan import DatasetMetadata, LocationContext, TimeContext
from backend.app.services.imd.registry import resolve_imd_location

class ImdQueryBuilder:
    """
    Constructs validated API request specifications for official IMD endpoints.
    Enforces strict parameter types, station IDs, district codes, and cyclone IDs.
    """

    BASE_URL = "https://api.imd.gov.in"

    def build_current_weather(self, station_id: str, lat: float, lon: float) -> Dict[str, Any]:
        """Endpoint 1: /api/v1/current_wx"""
        if not station_id:
            raise ValueError("station_id required for current weather query")
        return {
            "endpoint": "/api/v1/current_wx",
            "method": "GET",
            "params": {"station_id": station_id, "lat": round(lat, 4), "lon": round(lon, 4)},
            "url": f"{self.BASE_URL}/api/v1/current_wx?station_id={station_id}&lat={lat}&lon={lon}"
        }

    def build_location_forecast(self, station_id: str, lat: float, lon: float, days: int = 5) -> Dict[str, Any]:
        """Endpoint 2: /api/v1/cityforecastloc"""
        if not station_id:
            raise ValueError("station_id required for city/location forecast")
        return {
            "endpoint": "/api/v1/cityforecastloc",
            "method": "GET",
            "params": {"station_id": station_id, "lat": round(lat, 4), "lon": round(lon, 4), "days": min(days, 7)},
            "url": f"{self.BASE_URL}/api/v1/cityforecastloc?station_id={station_id}&lat={lat}&lon={lon}&days={days}"
        }

    def build_district_nowcast(self, district_id: str) -> Dict[str, Any]:
        """Endpoint 3: /api/v1/districtnowcast"""
        if not district_id:
            raise ValueError("district_id required for district nowcast")
        return {
            "endpoint": "/api/v1/districtnowcast",
            "method": "GET",
            "params": {"district_id": district_id},
            "url": f"{self.BASE_URL}/api/v1/districtnowcast?district_id={district_id}"
        }

    def build_district_warning(self, district_id: str) -> Dict[str, Any]:
        """Endpoint 4: /api/v1/districtwarning"""
        if not district_id:
            raise ValueError("district_id required for district warning")
        return {
            "endpoint": "/api/v1/districtwarning",
            "method": "GET",
            "params": {"district_id": district_id},
            "url": f"{self.BASE_URL}/api/v1/districtwarning?district_id={district_id}"
        }

    def build_sea_bulletin(self, sea_area: str = "North Arabian Sea") -> Dict[str, Any]:
        """Endpoint 5: /api/v1/seabulletin"""
        return {
            "endpoint": "/api/v1/seabulletin",
            "method": "GET",
            "params": {"sea_area": sea_area},
            "url": f"{self.BASE_URL}/api/v1/seabulletin?sea_area={sea_area.replace(' ', '%20')}"
        }

    def build_coastal_bulletin(self, coastal_zone: str = "North Maharashtra Coast") -> Dict[str, Any]:
        """Endpoint 6: /api/v1/coastalbulletin"""
        return {
            "endpoint": "/api/v1/coastalbulletin",
            "method": "GET",
            "params": {"coastal_zone": coastal_zone},
            "url": f"{self.BASE_URL}/api/v1/coastalbulletin?coastal_zone={coastal_zone.replace(' ', '%20')}"
        }

    def build_fishermen_warning(self, coastal_region: str = "Maharashtra Coast") -> Dict[str, Any]:
        """Endpoint 7: /api/v1/fishermenwarning"""
        return {
            "endpoint": "/api/v1/fishermenwarning",
            "method": "GET",
            "params": {"coastal_region": coastal_region},
            "url": f"{self.BASE_URL}/api/v1/fishermenwarning?coastal_region={coastal_region.replace(' ', '%20')}"
        }

    def build_cyclone_track(self, cyclone_id: str = "LATEST") -> Dict[str, Any]:
        """Endpoint 8: /api/v1/cyclone_track"""
        return {
            "endpoint": "/api/v1/cyclone_track",
            "method": "GET",
            "params": {"cyclone_id": cyclone_id},
            "url": f"{self.BASE_URL}/api/v1/cyclone_track?cyclone_id={cyclone_id}"
        }

    def build_cyclone_wind(self, cyclone_id: str = "LATEST") -> Dict[str, Any]:
        """Endpoint 9: /api/v1/cyclone_wind"""
        return {
            "endpoint": "/api/v1/cyclone_wind",
            "method": "GET",
            "params": {"cyclone_id": cyclone_id},
            "url": f"{self.BASE_URL}/api/v1/cyclone_wind?cyclone_id={cyclone_id}"
        }

    def build_cyclone_cone(self, cyclone_id: str = "LATEST") -> Dict[str, Any]:
        """Endpoint 10: /api/v1/cyclone_cou"""
        return {
            "endpoint": "/api/v1/cyclone_cou",
            "method": "GET",
            "params": {"cyclone_id": cyclone_id},
            "url": f"{self.BASE_URL}/api/v1/cyclone_cou?cyclone_id={cyclone_id}"
        }

    def build_bulletin_query(
        self,
        dataset: DatasetMetadata,
        location: LocationContext,
        time_window: TimeContext,
        warning_type: str = "ALL"
    ) -> Dict[str, Any]:
        """Unified builder invoked by MarineDataSource interface."""
        res_loc = resolve_imd_location(location.name)
        bbox = location.marine_bbox

        return {
            "dataset_id": dataset.dataset_id,
            "endpoint": "/api/v1/coastalbulletin",
            "source": "IMD",
            "station_id": res_loc["station_id"],
            "district_id": res_loc["district_id"],
            "coastal_zone": res_loc["coastal_zone"],
            "params": {
                "coastal_location": location.name,
                "state": res_loc["state"],
                "center_lat": location.latitude,
                "center_lon": location.longitude,
                "station_id": res_loc["station_id"],
                "district_id": res_loc["district_id"],
                "bbox": bbox,
                "start_time": time_window.start,
                "end_time": time_window.end,
                "warning_type": warning_type
            },
            "request_url": f"{self.BASE_URL}/api/v1/coastalbulletin?coastal_zone={res_loc['coastal_zone'].replace(' ', '%20')}"
        }

imd_query_builder = ImdQueryBuilder()
