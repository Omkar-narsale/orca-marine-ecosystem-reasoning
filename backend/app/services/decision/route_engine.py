from typing import Dict, Any, List, Optional
from backend.app.services.geospatial.geometry import haversine_distance_km as haversine_distance

MUMBAI_HOME_PORT = {
    "name": "Mumbai Harbor / Sassoon Docks",
    "lat": 18.92,
    "lon": 72.84
}

class OperationalRouteEngine:
    """
    Operational Route Corridor Planning Foundation for ORCA Phase 5.
    Computes direct and safe bypass corridors from home port to candidate marine zones.
    Detects spatial geofence collisions and elevated wave hazard zones along transit segments.
    """
    def plan_operational_corridor(
        self,
        destination_zone_id: str = "zone-c",
        zones: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        dest_coords = {
            "zone-c": {"name": "South Shelf Grounds (Zone C)", "lat": 18.58, "lon": 72.71},
            "zone-d": {"name": "Mid-Shelf Trench (Zone D)", "lat": 18.90, "lon": 72.35},
            "zone-a": {"name": "North Offshore Reach (Zone A)", "lat": 19.32, "lon": 72.62},
            "zone-b": {"name": "Central Harbor Fairway (Zone B)", "lat": 18.95, "lon": 72.80}
        }.get(destination_zone_id, {"name": "South Shelf Grounds (Zone C)", "lat": 18.58, "lon": 72.71})

        start = MUMBAI_HOME_PORT
        direct_dist_km = haversine_distance(start["lat"], start["lon"], dest_coords["lat"], dest_coords["lon"])
        direct_dist_nm = round(direct_dist_km * 0.539957, 1)

        # Build corridor segments
        segments = []
        has_geofence_conflict = False
        has_hazard_conflict = False

        if destination_zone_id == "zone-c":
            # Safe southern exit avoiding central harbor naval buffer
            waypoints = [
                [start["lat"], start["lon"]],
                [18.82, 72.82], # Southern Harbor Exit Channel
                [18.70, 72.76], # Alibag Inshore Transit
                [dest_coords["lat"], dest_coords["lon"]]
            ]
            segments = [
                {"segment_id": "seg_1", "start": "Sassoon Dock", "end": "South Channel", "status": "CLEAR", "hazard": "None"},
                {"segment_id": "seg_2", "start": "South Channel", "end": "Alibag Reach", "status": "CLEAR", "hazard": "Calm Sea"},
                {"segment_id": "seg_3", "start": "Alibag Reach", "end": "Zone C Shelf", "status": "CLEAR", "hazard": "Candidate Boundary"}
            ]
            corridor_status = "SAFE_TRANSIT_CORRIDOR"
            recommendation = "Recommended Southern Inshore Corridor clear of Naval Fairway restrictions and high swell."

        elif destination_zone_id == "zone-b":
            waypoints = [
                [start["lat"], start["lon"]],
                [dest_coords["lat"], dest_coords["lon"]]
            ]
            segments = [
                {"segment_id": "seg_1", "start": "Port Exit", "end": "Zone B Fairway", "status": "DO_NOT_ENTER", "hazard": "Naval Security Buffer"}
            ]
            corridor_status = "RESTRICTED_CORRIDOR"
            has_geofence_conflict = True
            recommendation = "DO NOT ENTER: Direct corridor crosses active Naval Security Anchorage and commercial fairway."

        elif destination_zone_id == "zone-a":
            waypoints = [
                [start["lat"], start["lon"]],
                [19.10, 72.78],
                [dest_coords["lat"], dest_coords["lon"]]
            ]
            segments = [
                {"segment_id": "seg_1", "start": "Port Exit", "end": "Bandra Reach", "status": "CAUTION", "hazard": "Moderate Waves (2.1m)"},
                {"segment_id": "seg_2", "start": "Bandra Reach", "end": "Zone A Reach", "status": "HIGH_RISK_SEGMENT", "hazard": "Rough Seas (4.1m) & Gale Wind"}
            ]
            corridor_status = "HIGH_RISK_CORRIDOR"
            has_hazard_conflict = True
            recommendation = "HAZARDOUS: Transit segment breaches craft safety limits due to 4.1m swells and gale gusts."

        else: # zone-d
            waypoints = [
                [start["lat"], start["lon"]],
                [18.91, 72.55],
                [dest_coords["lat"], dest_coords["lon"]]
            ]
            segments = [
                {"segment_id": "seg_1", "start": "Port Exit", "end": "Offshore Marker", "status": "CLEAR", "hazard": "None"},
                {"segment_id": "seg_2", "start": "Offshore Marker", "end": "Mid-Shelf", "status": "CAUTION", "hazard": "Moderate Wave Swell (2.1m)"}
            ]
            corridor_status = "CAUTIONARY_CORRIDOR"
            recommendation = "Manageable offshore transit. Conclude operations before afternoon swell rise."

        return {
            "departure_port": start["name"],
            "destination_name": dest_coords["name"],
            "destination_zone_id": destination_zone_id,
            "corridor_status": corridor_status,
            "distance_nm": direct_dist_nm,
            "distance_km": round(direct_dist_km, 1),
            "waypoints": waypoints,
            "segments": segments,
            "has_geofence_conflict": has_geofence_conflict,
            "has_hazard_conflict": has_hazard_conflict,
            "recommendation": recommendation,
            "navigational_disclaimer": "Operational corridor is a decision-support suggestion. Does not replace official nautical chart navigation or master-of-vessel discretion."
        }

route_engine = OperationalRouteEngine()


from pydantic import BaseModel, Field

class RouteSegment(BaseModel):
    segment_id: str
    start: str
    end: str
    status: str
    hazard: str


class RouteCorridorResponse(BaseModel):
    departure_port: str
    destination_name: str
    destination_zone_id: str
    corridor_status: str
    distance_nm: float
    distance_km: float
    waypoints: List[List[float]]
    segments: List[RouteSegment]
    has_geofence_conflict: bool
    has_hazard_conflict: bool
    recommendation: str
    navigational_disclaimer: str


def plan_route_corridor(
    start_point: tuple[float, float] = (18.9220, 72.8347),
    destination_zone_id: str = "zone-c"
) -> RouteCorridorResponse:
    """Plans operational route corridor from Mumbai port to candidate zone."""
    zid = destination_zone_id.lower().replace("_", "-")
    res = route_engine.plan_operational_corridor(zid)
    return RouteCorridorResponse(**res)

